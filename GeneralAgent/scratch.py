# 短期记忆(short-term memory)

from tinydb import TinyDB, Query

# 思维火花节点
class SparkNode:

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['node_id'], dict['role'], dict['type'], dict['state'], dict['name'], dict['value'], dict['command'], dict['parent'], dict['childrens'])

    def __init__(self, node_id, role, type, state, name, value, command, parent=None, childrens=[]):
        assert role in ['user', 'system']
        assert type in ['input', 'output', 'plan', 'think', 'write_code', 'run_code']
        assert state in ['ready', 'working', 'success', 'fail']
        self.node_id = node_id
        self.role = role
        self.type = type
        self.state = state
        self.name = name
        self.value = value
        self.command = command
        self.parent = parent
        self.childrens = childrens

    def __str__(self):
        return f'role: {self.role}, type: {self.type}, state: {self.state}, name: {self.name}, value: {self.value}, command: {self.command}'


# 短期记忆
class Scratch:
    def __init__(self, file_path='./memory.json'):
        self.db = TinyDB(file_path)
        self.spark_node_list = [SparkNode(node) for node in self.db.all()]

    def new_node_id(self):
        return len(self.new_node_id)