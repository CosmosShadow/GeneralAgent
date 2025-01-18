import sqlite3
import json
import logging
from GeneralAgent.utils import encode_image

class SQLiteMemory:
    def __init__(self, serialize_path='./memory.db', messages=[]):
        """
        @db_path: str, SQLite数据库路径，默认为'./memory.db'
        """
        self.db_path = serialize_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()
        
        if len(messages) > 0:
            self._validate_messages(messages)
            for msg in messages:
                self.add_message(msg['role'], msg['content'])

    def _create_table(self):
        """创建messages表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_message(self, role, content):
        """添加新消息"""
        assert role in ['user', 'system', 'assistant']
        
        if isinstance(content, list):
            # 处理多模态内容
            r = []
            for c in content:
                if isinstance(c, dict):
                    if 'image' in c:
                        r.append({'type': 'image_url', 'image_url': {'url': encode_image(c['image'])}})
                    elif 'text' in c:
                        r.append({'type': 'text', 'text': c['text']})
                    else:
                        raise Exception('message type wrong')
                else:
                    r.append({'type': 'text', 'text': c})
            content = json.dumps(r)
        
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        self.conn.commit()
        return cursor.lastrowid

    def append_message(self, role, content, message_id=None):
        """追加消息内容"""
        cursor = self.conn.cursor()
        
        if message_id is not None:
            # 更新指定消息
            cursor.execute('SELECT role, content FROM messages WHERE id = ?', (message_id,))
            result = cursor.fetchone()
            if not result or result[0] != role:
                raise ValueError("Invalid message_id or role mismatch")
            
            new_content = result[1] + '\n' + content
            cursor.execute('UPDATE messages SET content = ? WHERE id = ?', (new_content, message_id))
            # 删除该消息之后的所有消息
            cursor.execute('DELETE FROM messages WHERE id > ?', (message_id,))
        else:
            # 追加到最后一条相同role的消息
            cursor.execute('SELECT id, content FROM messages WHERE role = ? ORDER BY id DESC LIMIT 1', (role,))
            last_message = cursor.fetchone()
            
            if last_message:
                new_content = last_message[1] + '\n' + content
                cursor.execute('UPDATE messages SET content = ? WHERE id = ?', (new_content, last_message[0]))
            else:
                cursor.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        
        self.conn.commit()
        return cursor.lastrowid

    def get_messages(self):
        """获取所有消息"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT role, content FROM messages ORDER BY id')
        messages = []
        for row in cursor.fetchall():
            content = row[1]
            try:
                # 尝试解析JSON格式的多模态内容
                content = json.loads(content)
            except json.JSONDecodeError:
                pass
            messages.append({'role': row[0], 'content': content})
        return messages

    def recover(self, index):
        """恢复到指定索引的状态"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM messages WHERE id > ?', (index,))
        self.conn.commit()

    def show_messages(self):
        """显示所有消息"""
        logging.info('-' * 50 + '<Memory>' + '-' * 50)
        for message in self.get_messages():
            content = message['content']
            if isinstance(content, (dict, list)):
                content = json.dumps(content)
            logging.info('[[' + message['role'] + ']]: ' + str(content)[:100])
        logging.info('-' * 50 + '</Memory>' + '-' * 50)

    def _validate_messages(self, messages):
        """验证消息格式"""
        for message in messages:
            assert isinstance(message, dict), 'message format wrong'
            assert 'role' in message, 'message format wrong'
            assert 'content' in message, 'message format wrong'
            assert message['role'] in ['user', 'assistant'], 'message format wrong'

    def __del__(self):
        """析构函数，确保关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close() 

def test_SQLiteMemory():
    import os
    serialize_path = './sqlite_memory.db'
    
    # 确保开始测试前文件不存在
    if os.path.exists(serialize_path):
        try:
            os.remove(serialize_path)
        except PermissionError:
            print("警告：无法删除已存在的数据库文件，可能被其他程序占用")
            return

    try:
        # 测试基本的添加消息
        mem = SQLiteMemory(serialize_path=serialize_path)
        mem.add_message('user', 'hello')
        mem.add_message('assistant', 'hi')
        assert len(mem.get_messages()) == 2, "应该有2条消息"
        
        # 显式关闭第一个连接
        mem.conn.close()
        
        # 测试消息持久化
        mem2 = SQLiteMemory(serialize_path=serialize_path)
        assert len(mem2.get_messages()) == 2, "加载后应该有2条消息"
        
        # 测试append_message的合并行为
        mem2.append_message('assistant', 'hi')
        assert len(mem2.get_messages()) == 2, "append后应该仍然是2条消息"
        assert mem2.get_messages()[-1]['content'] == 'hi\nhi', "最后一条消息应该被合并"
        
        # 显式关闭第二个连接
        mem2.conn.close()

    finally:
        # 确保在测试结束后清理，即使测试失败也会执行
        try:
            if os.path.exists(serialize_path):
                os.remove(serialize_path)
        except PermissionError:
            print("警告：无法删除数据库文件，请手动删除")

if __name__ == '__main__':
    # 运行测试
    print("开始运行测试...")
    test_SQLiteMemory()
    print("测试完成！")
