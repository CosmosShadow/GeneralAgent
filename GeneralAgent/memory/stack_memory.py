# Memeory
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query


@dataclass
class StackMemoryNode:
    role: str
    action: str
    state: str = 'ready'
    content: str = None
    prefix: str = None
    node_id: int = None
    parent: int = None
    childrens: List[int] = None

    def __post_init__(self):
        assert self.role in ['user', 'system', 'root'], self.role
        assert self.action in ['input', 'answer', 'plan'], self.action
        assert self.state in ['ready', 'success', 'fail'], self.state
        self.childrens = self.childrens if self.childrens else []

    def __str__(self):
        return f'<{self.role}><{self.action}><{self.state}>: {self.content}'
    
    def __repr__(self):
        return str(self)

    def success_work(self):
        self.state = 'success'

    def fail_work(self):
        self.state = 'fail'

    def is_root(self):
        return self.role == 'root'
    
    def get_level(self):
        if self.is_root():
            return 0
        else:
            return self.get_parent().get_level() + 1
    
    @classmethod
    def new_root(cls):
        return cls(node_id=0, role='root', action='input', state='success', content='root', parent=None, childrens=[])


class StackMemory:
    def __init__(self, serialize_path='./memory.json'):
        self.db = TinyDB(serialize_path)
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
            # print(node_id)
            # print(self)
            self.current_node = self.get_node(node_id)
        else:
            self.current_node = None

    def set_current_node(self, current_node):
        self.current_node = current_node
        # save current node
        self.db.table('current_node').truncate()
        self.db.table('current_node').insert({'id': current_node.node_id})

    def new_node_id(self):
        return max(self.spark_nodes.keys()) + 1
    
    def node_count(self):
        # ignore root node
        return len(self.spark_nodes.keys()) - 1
        
    def is_all_children_success(self, node):
        # check if all childrens of node are success
        childrens = [self.get_node(node_id) for node_id in node.childrens]
        return all([children.state == 'success' for children in childrens])

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
    
    def get_related_nodes_for_node(self, node):
        # ancestors + left_brothers + self
        parent = self.get_node_parent(node)
        brothers = [self.get_node(node_id) for node_id in parent.childrens]
        left_brothers = [('brother', x) for x in brothers[:brothers.index(node)]]
        ancestors = self.get_related_nodes_for_node(parent) if not parent.is_root() else []
        return ancestors + left_brothers + [('direct', node)]
    
    def get_related_messages_for_node(self, node: StackMemoryNode):
        def _get_message(node, position='direct'):
            content = node.content if node.prefix is None else node.prefix + ' ' + node.content
            if position == 'brother' and node.action == 'plan' and len(node.childrens) > 0:
                content = node.content + ' [detail ...]'
            return {'role': node.role, 'content': content}
        nodes_with_position = self.get_related_nodes_for_node(node)
        messages = [_get_message(node, position) for position, node in nodes_with_position]
        # if node.action == 'plan':
        #     messages[-1]['content'] = 'Improve the details of this topic:: ' + messages[-1]['content']
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
    
    def success_node(self, node):
        node.success_work()
        self.update_node(node)
    
    def _get_todo_node(self, node=None):
        # get the first ready node in the tree of node
        if node is None:
            node = self.get_node(0)
        for node_id in node.childrens:
            child = self._get_todo_node(self.get_node(node_id))
            if child is not None:
                return child
        if node.is_root():
            return None
        if node.state in ['ready']:
            return node
        return None
    
    def get_todo_node(self):
        todo_node = self._get_todo_node()
        # if all childrens of todo_node are success, success todo_node
        if todo_node is not None and len(todo_node.childrens) > 0 and self.is_all_children_success(todo_node):
            self.success_node(todo_node)
            return self.get_todo_node()
        return todo_node