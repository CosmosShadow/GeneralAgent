# 短期记忆(short-term memory)

from tinydb import TinyDB, Query

# 思维火花节点
class SparkNode:

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['node_id'], dict['role'], dict['action'], dict['state'], dict['task'], dict['input'], dict['output'], dict['parent'], dict['childrens'])

    def __init__(self, node_id, role, action, state, task, input, output, parent=None, childrens=[]):
        assert role in ['user', 'system']
        assert action in ['input', 'output', 'plan', 'think', 'write_code', 'run_code']
        assert state in ['ready', 'working', 'success', 'fail']
        self.node_id = node_id
        self.role = role
        self.action = action
        self.state = state
        self.task = task
        self.input = input
        self.output = output
        self.parent = parent
        self.childrens = childrens

    def __str__(self):
        return f'role: {self.role}, action: {self.action}, state: {self.state}, task: {self.task}, input: {self.input}, output: {self.output}'


# 短期记忆
class Scratch:
    def __init__(self, file_path='./memory.json'):
        self.db = TinyDB(file_path)
        self.spark_node_list = [SparkNode(node) for node in self.db.all()]
    
    def add_node(self, role, action, state, task, input, output, parent, childrens):
        # TODO: parent和childrens需要设置
        node_id = len(self.spark_node_list)
        node = SparkNode(node_id, role, action, state, task, input, output, parent, childrens)
        self.db.insert(node.__dict__)
        return node
    
    def get_node(self, node_id):
        return self.spark_node_list[node_id]
    
    def update_node(self, node):
        self.db.update(node.__dict__, Query().node_id == node.node_id)
    
    def get_node_enviroment(self, node):
        # 获取节点环境，返回节点上左右下的节点描述(string)
        lines = []
        parent = self.get_node(node.parent) if node.parent else None
        if parent:
            lines.append(f'parent: {str(parent)}')
            brothers = [self.get_node(node_id) for node_id in parent.childrens]
            left_brothers = brothers[:brothers.index(node)]
            right_brothers = brothers[brothers.index(node)+1:]
            for left_brother in left_brothers:
                lines.append(f'left_brother: {str(left_brother)}')
            lines.append('self: ' + str(node))
            for right_brother in right_brothers:
                lines.append(f'right_brother: {str(right_brother)}')
        childrens = [self.get_node(node_id) for node_id in node.childrens]
        for children in childrens:
            lines.append(f'children: {str(children)}')
        return '\n'.join(lines)