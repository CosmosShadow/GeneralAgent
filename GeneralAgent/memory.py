# Memeory
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
from GeneralAgent.llm import num_tokens_from_messages

# 记忆节点
@dataclass
class MemoryNode:
    role: str
    # 核心内容
    action: str
    state: str = 'ready'
    content: str = None
    # 记忆/工作堆栈需要的属性
    node_id: int = None
    parent: int = None
    childrens: List[int] = None

    def __post_init__(self):
        assert self.role in ['user', 'system', 'root'], self.role   # 主要用于用来标识root, input属于user，其他都属于system
        assert self.action in ['input', 'answer', 'plan'], self.action
        assert self.state in ['ready', 'working', 'success', 'fail'], self.state
        self.childrens = self.childrens if self.childrens else []

    def get_message(self, position='direct'):
        content = self.content
        if position == 'brother' and self.action == 'plan' and len(self.childrens) > 0:
            content = self.content + ' [detail ...]'
        return {'role': self.role, 'content': content}

    def __str__(self):
        return f'<{self.role}><{self.action}><{self.state}>: {self.content}'
    
    def __repr__(self):
        return str(self)

    def start_work(self):
        self.state = 'working'

    def success_work(self):
        self.state = 'success'

    def fail_work(self):
        self.state = 'fail'

    def is_root(self):
        return self.role == 'root'
    
    def get_level(self):
        # 获取级别
        if self.is_root():
            return 0
        else:
            return self.get_parent().get_level() + 1
    
    @classmethod
    def new_root(cls):
        return cls(node_id=0, role='root', action='input', state='success', content='root', parent=None, childrens=[])


class Memory:
    def __init__(self, file_path='./memory.json'):
        self.db = TinyDB(file_path)
        nodes = [MemoryNode(**node) for node in self.db.all()]
        self.spark_nodes = dict(zip([node.node_id for node in nodes], nodes))
        # add root node
        if len(self.spark_nodes) == 0:
            root_node = MemoryNode.new_root()
            self.spark_nodes[root_node.node_id] = root_node
            self.db.insert(root_node.__dict__)

    def new_node_id(self):
        return max(self.spark_nodes.keys()) + 1

    def node_count(self):
        return len(self.spark_nodes) - 1
    
    def is_last_node_of_parent(self, node):
        # 判断是否是父节点的最后一个节点
        parent = self.get_node_parent(node)
        if parent:
            return parent.childrens[-1] == node.node_id
        else:
            return False
        
    def is_all_children_success(self, node):
        # 判断是否所有子节点都成功
        childrens = [self.get_node(node_id) for node_id in node.childrens]
        return all([children.state == 'success' for children in childrens])

    def add_node(self, node):
        # 保持节点，不说明位置，默认添加到根节点下
        root_node = self.get_node(0)
        node.node_id = self.new_node_id()
        node.parent = root_node.node_id
        root_node.childrens.append(node.node_id)
        self.update_node(root_node)
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
    
    def add_node_after(self, last_node, node):
        # 将node添加到last_node同级别的后面
        node.node_id = self.new_node_id()
        node.parent = last_node.parent
        # 更新父节点关系
        parent = self.get_node_parent(node)
        if parent:
            parent.childrens.insert(parent.childrens.index(last_node.node_id)+1, node.node_id)
            self.update_node(parent)
        # 将last_node节点的children迁移到node里面
        node.childrens = last_node.childrens
        last_node.childrens = []
        self.update_node(last_node)
        # 更新子节点的父节点关系
        for children_id in node.childrens:
            children = self.get_node(children_id)
            children.parent = node.node_id
            self.update_node(children)
        # 保存自己: 数据库 + 内存
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
        return node
    
    def add_node_in(self, parent_node, node, put_first=False):
        # 添加节点node到parent_node的子节点中, 默认添加到最后，但put_first=True时，添加到最前面
        node.node_id = self.new_node_id()
        node.parent = parent_node.node_id
        # 更新父节点关系
        if put_first:
            parent_node.childrens.insert(0, node.node_id)
        else:
            parent_node.childrens.append(node.node_id)
        self.update_node(parent_node)
        # 保存自己: 数据库 + 内存
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
        return node
    
    def insert_node_in(self, parent_node, node):
        # 添加node节点成为parent_node的子节点，且将原本parent_node的子节点迁移到node的子节点中
        node.node_id = self.new_node_id()
        node.parent = parent_node.node_id
        # 更新父节点关系
        node.childrens = parent_node.childrens
        parent_node.childrens = [node.node_id]
        self.update_node(parent_node)
        # 更新子节点的父节点关系
        for children_id in node.childrens:
            children = self.get_node(children_id)
            children.parent = node.node_id
            self.update_node(children)
        # 保存自己: 数据库 + 内存
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
        return node
        
    
    def delete_node(self, node, update_parent=True):
        # 删除父节点关系
        parent = self.get_node_parent(node)
        if parent and update_parent:
            parent.childrens.remove(node.node_id)
            self.update_node(parent)
        # 删除所有子节点
        childrens = [self.get_node(node_id) for node_id in node.childrens]
        for children in childrens:
            self.delete_node(children, update_parent=False)
        # 删除自己: 数据库删除 + 内存删除
        self.db.remove(Query().node_id == node.node_id)
        self.spark_nodes.pop(node.node_id)

    def delete_after_node(self, node):
        # 删除节点后面的所有节点
        parent = self.get_node_parent(node)
        if parent:
            brothers = [self.get_node(node_id) for node_id in parent.childrens]
            right_brothers = brothers[brothers.index(node)+1:]
            for right_brother in right_brothers:
                self.delete_node(right_brother, update_parent=False)
                parent.childrens.remove(right_brother.node_id)
            # 更新父节点
            self.update_node(parent)
    
    def get_node(self, node_id):
        return self.spark_nodes[node_id]
    
    def get_node_level(self, node:MemoryNode):
        # 获取节点的级别
        if node.is_root():
            return 0
        else:
            return self.get_node_level(self.get_node_parent(node)) + 1
    
    def get_node_parent(self, node):
        if node.parent is None:
            return None
        else:
            return self.get_node(node.parent)
    
    def update_node(self, node):
        self.db.update(node.__dict__, Query().node_id == node.node_id)

    def get_messages_for_node(self, node, head_token_limit=2000, brother_token_limit=2000):
        parent = self.get_node_parent(node)
        # 遍历head
        head_messages = []
        head = parent
        while not head.is_root():
            if num_tokens_from_messages([head.get_message()] + head_messages) < head_token_limit:
                head_messages = [head.get_message()] + head_messages
                head = self.get_node_parent(head)
            else:
                break
        # 取合适的left brothers
        brother_messages = []
        brothers = [self.get_node(node_id) for node_id in parent.childrens]
        left_brothers = brothers[:brothers.index(node)]
        left_brothers.reverse()
        for left_brother in left_brothers:
            if num_tokens_from_messages([left_brother.get_message()] + brother_messages) < brother_token_limit:
                brother_messages = [left_brother.get_message()] + brother_messages
            else:
                break
        # 自身的message
        self_message = node.get_message()
        # 合并: heads + brothers + self
        messages = head_messages + brother_messages + [self_message]
        return messages
    
    def get_related_nodes_for_node(self, node):
        # 获取相关的节点
        parent = self.get_node_parent(node)
        brothers = [self.get_node(node_id) for node_id in parent.childrens]
        left_brothers = [('brother', x) for x in brothers[:brothers.index(node)]]
        # 父节点相关节点 + 左边兄弟节点 + 自己
        ancestors = self.get_related_nodes_for_node(parent) if not parent.is_root() else []
        return ancestors + left_brothers + [('direct', node)]
    
    def get_related_messages_for_node(self, node):
        # 获取相关的消息
        nodes_with_position = self.get_related_nodes_for_node(node)
        messages = [node.get_message(position) for position, node in nodes_with_position]
        if node.action == 'plan':
            messages[-1]['content'] = '完善这个topic的细节: ' + messages[-1]['content']
        return messages
    
    def get_all_description_of_node(self, node, intend_char='    ', depth=0):
        # 获取节点描述，包括子节点
        lines = []
        description = intend_char * depth + str(node)
        if not node.is_root():
            lines += [description]
        for children_id in node.childrens:
            children = self.get_node(children_id)
            lines += self.get_all_description_of_node(children, intend_char, depth+1)
        return lines
    
    def __str__(self) -> str:
        lines = self.get_all_description_of_node(self.get_node(0), depth=-1)
        return '\n'.join(lines)
        # return '\n'.join([str(node) for k, node in self.spark_nodes.items()])
    
    def success_node(self, node):
        # 完成节点
        node.success_work()
        self.update_node(node)

    def fail_node(self, node):
        # 节点失败
        node.fail_work()
        self.update_node(node)

    def start_todo_node(self, node):
        # 节点开始工作
        node.start_work()
        self.update_node(node)

    def get_next_plan_node(self):
        for node in self.spark_nodes.values():
            if node.state in ['ready', 'working'] and node.action == 'plan':
                return node
        return None
    
    def get_todo_node(self, node=None):
        # 查找todo节点: 从根节点开始，找到最深的第一个ready或working的节点
        if node is None:
            node = self.get_node(0)
        for node_id in node.childrens:
            child = self.get_todo_node(self.get_node(node_id))
            if child is not None:
                return child
        if node.is_root():
            return None
        if node.state in ['ready', 'working']:
            return node
        return None