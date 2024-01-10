from base_setting import *
import websockets
import logging
import json
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid

@dataclass
class Message():
    type: Optional[str] = 'message' # token | message
    id: Optional[str] = None
    role: Optional[str] = ''               # user / bot
    bot_id: Optional[str] = ''           # bot id
    chat_id: Optional[str] = ''          # chat id
    create_at: Optional[str] = None
    msg: Optional[str] = ''
    file: Optional[str] = ''
    ui: Optional[str] = ''      # UI组件(js, name, data)
    extention: Optional[str] = None     # 扩展字段

    def __post_init__(self):
        if self.create_at is None:
            self.create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        if self.id is None:
            self.id = str(uuid.uuid4())

    def response_template(self, is_token=False):
        new_message = Message(
            role='bot',
            bot_id=self.bot_id,
            chat_id=self.chat_id,
            type='token' if is_token else 'message',
        )
        return new_message
    
    def to_text(self):
        data = {
            'type': 'message',
            'data': self.__dict__
        }
        return json.dumps(data)


@pytest.mark.asyncio
async def test_user_chat():
    bot_id = 'hello'
    clear_bot(bot_id)
    ws_url = WS_HOST + "/ws/user/"
    async with websockets.connect(ws_url) as ws:
        # 发送消息
        msg = '1 + 1 = ?'
        message = Message(bot_id=bot_id, msg=msg)
        await ws.send(message.to_text())
        logging.debug('send message success')
        # 接收消息，
        # 第一条: 发送成功的消息
        res = await ws.recv()
        message: Message = Message(**json.loads(res)['data'])
        logging.debug(message)
        logging.debug(message)
        assert msg.strip() == message.msg.strip()
        assert message.chat_id != ''
        # 回复消息: token + message
        result = ''
        msg_id = None
        while True:
            res = await ws.recv()
            obj = json.loads(res)
            if obj['type'] == 'message':
                message = Message(**obj['data'])
                if message.type == 'token':
                    result += message.msg
                    msg_id = message.id
                    continue
                else:
                    assert result == message.msg
                    assert 'hello' in message.msg
                    assert msg_id is not None
                    logging.debug(msg_id, message.id)
                    assert msg_id == message.id
                    break
    # 获取chats列表
    chats = get_chats(bot_id)
    assert len(chats) == 1
    chat_id = chats[0]['id']
    # 获取messages列表
    messages = get_messages(bot_id, chat_id)
    assert len(messages) == 2
    clear_bot(bot_id)

if __name__ == '__main__':
    asyncio.run(test_user_chat())