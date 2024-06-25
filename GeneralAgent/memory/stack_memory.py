# Memeory
import json
from dataclasses import dataclass
from typing import List, Union
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


@dataclass
class StackMemoryNode:
    role: str
    type: str = None # 'text' or 'list'
    content: str = None
    node_id: int = None
    parent: int = None
    childrens: List[int] = None

    def __post_init__(self):
        assert self.role in ['user', 'system', 'root', 'assistant'], self.role
        self.childrens = self.childrens if self.childrens else []
        if self.type is None:
            self.type = 'text'

    def __str__(self):
        return f'<{self.role}><{self.type}>: {self.content}'
    
    def __repr__(self):
        return str(self)

    def is_root(self):
        return self.role == 'root'
    
    @classmethod
    def new_root(cls):
        return cls(node_id=0, role='root', content='root', parent=None, childrens=[])


class StackMemory:
    def __init__(self, serialize_path='./memory.json'):
        """
        @serialize_path: str, 序列化路径，默认为'./memory.json'。如果为None，则使用内存存储
        """
        if serialize_path is not None:
            self.db = TinyDB(serialize_path)
        else:
            # 内存存储，不序列化
            self.db = TinyDB(storage=MemoryStorage)
        nodes = [StackMemoryNode(**node) for node in self.db.all()]
        self.spark_nodes = dict(zip([node.node_id for node in nodes], nodes))
        # add root node
        if len(self.spark_nodes) == 0:
            root_node = StackMemoryNode.new_root()
            self.spark_nodes[root_node.node_id] = root_node
            self.db.insert(root_node.__dict__)
        # load current_node
        current_nodes = self.db.table('current_node').all()
        if len(current_nodes) > 0:
            node_id = current_nodes[0]['id']
            self.current_node = self.get_node(node_id)
        else:
            self.current_node = self.get_node(0)
        self.next_position = 'after' # 'after' or 'in'
        if self.current_node.is_root():
            self.next_position = 'in'

    def set_current_node(self, current_node):
        self.current_node = current_node
        # save current node
        self.db.table('current_node').truncate()
        self.db.table('current_node').insert({'id': current_node.node_id})
        # 同步数据库

    def new_node_id(self):
        return max(self.spark_nodes.keys()) + 1
    
    def node_count(self):
        # ignore root node
        return len(self.spark_nodes.keys()) - 1

    def add_node(self, node):
        # put in root node
        root_node = self.get_node(0)
        node.node_id = self.new_node_id()
        node.parent = root_node.node_id
        root_node.childrens.append(node.node_id)
        # save node
        self.update_node(root_node)
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node

    def delete_node(self, node):
        # delete node and all its childrens
        for children_id in node.childrens:
            children = self.get_node(children_id)
            self.delete_node(children)
        parent = self.get_node_parent(node)
        if parent:
            parent.childrens.remove(node.node_id)
            self.update_node(parent)
        self.db.remove(Query().node_id == node.node_id)
        del self.spark_nodes[node.node_id]

    
    def add_node_after(self, last_node, node):
        # add node after last_node
        node.node_id = self.new_node_id()
        node.parent = last_node.parent
        parent = self.get_node_parent(node)
        if parent:
            parent.childrens.insert(parent.childrens.index(last_node.node_id)+1, node.node_id)
            self.update_node(parent)
        # move childrens of last_node to node
        node.childrens = last_node.childrens
        last_node.childrens = []
        self.update_node(last_node)
        for children_id in node.childrens:
            children = self.get_node(children_id)
            children.parent = node.node_id
            self.update_node(children)
        # save node
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
        return node
    
    def add_node_in(self, parent_node, node, put_first=False):
        # add node in parent_node
        node.node_id = self.new_node_id()
        node.parent = parent_node.node_id
        if put_first:
            parent_node.childrens.insert(0, node.node_id)
        else:
            parent_node.childrens.append(node.node_id)
        self.update_node(parent_node)
        # save node
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
        return node
    
    def get_node(self, node_id):
        return self.spark_nodes[node_id]
    
    def get_node_level(self, node:StackMemoryNode):
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

    def get_level(self, node):
        if node.is_root():
            return 0
        else:
            return self.get_level(self.get_node_parent(node)) + 1
    
    def get_related_nodes_for_node(self, node):
        # ancestors + left_brothers + self
        parent = self.get_node_parent(node)
        brothers = [self.get_node(node_id) for node_id in parent.childrens]
        left_brothers = [('brother', x) for x in brothers[:brothers.index(node)]]
        if self.get_level(parent) != 0:
            left_brothers = left_brothers[-4:]
        ancestors = self.get_related_nodes_for_node(parent) if not parent.is_root() else []
        return ancestors + left_brothers + [('direct', node)]
    
    def get_related_messages_for_node(self, node: StackMemoryNode):
        # 获取节点相关的消息列表(OpenAI格式，包含图片)
        def _encode_image(image_path):
            if image_path.startswith('http'):
                return image_path
            import base64
            with open(image_path, "rb") as image_file:
                bin_data = base64.b64encode(image_file.read()).decode('utf-8')
            image_type = image_path.split('.')[-1].lower()
            virtural_url = f"data:image/{image_type};base64,{bin_data}"
            return virtural_url
        nodes_with_position = self.get_related_nodes_for_node(node)
        def _parse_node(node):
            if node.type == 'list':
                contents = []
                items = json.loads(node.content)
                for item in items:
                    if isinstance(item, str):
                        contents.append({'type': 'text', 'text': item})
                    elif isinstance(item, dict):
                        key = list(item.keys())[0]
                        if key == 'image':
                            url = _encode_image(item[key]) 
                            contents.append({'type': 'image_url', "image_url": { "url": url}})
                        elif key == 'text':
                            contents.append({'type': 'text', 'text': item[key]})
                        else:
                            raise Exception('message type wrong')
                    else:
                        raise Exception('message type wrong')
                return {'role': node.role, 'content': contents}
            return {'role': node.role, 'content': node.content}
        messages = [_parse_node(node) for position, node in nodes_with_position]
        return messages
    
    def get_all_description_of_node(self, node, intend_char='    ', depth=0):
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
    
    def get_messages(self):
        return self.get_related_messages_for_node(self.current_node)

    def push_stack(self):
        self.next_position = 'in'
        return self.current_node.node_id

    def add_message(self, role, message: Union[str, list]):
        assert role in ['user', 'system', 'assistant'], role
        type = 'text'
        if isinstance(message, list):
            type = 'list'
            message = json.dumps(message)
        new_node = StackMemoryNode(role=role, content=message, type=type)
        if self.next_position == 'after':
            self.add_node_after(self.current_node, new_node)
        else:
            self.add_node_in(self.current_node, new_node)
        self.next_position = 'after'
        self.set_current_node(new_node)
        return new_node.node_id
    
    def append_message(self, role, message, message_id=None):
        if message_id is None:
            message_id = self.current_node.node_id
        node_id = message_id
        self.pop_stack_to(node_id)
        node = self.get_node(node_id)
        node.content += '\n' + message
        self.update_node(node)
        self.set_current_node(node)
        return node.node_id

    def pop_stack(self):
        if self.next_position == 'in':
            self.next_position = 'after'
        else:
            self.set_current_node(self.get_node_parent(self.current_node))
            self.next_position = 'after'
            return self.current_node.node_id
    
    def pop_stack_to(self, node_id):
        self.set_current_node(self.get_node(node_id))
        self.next_position = 'after'
        return self.current_node.node_id