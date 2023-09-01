# 短期记忆(short-term memory)
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query

# 思维火花节点
@dataclass
class SparkNode:
    role: str
    action: str
    state: str = 'ready'

    content: str = None
    input: str = None
    output: str = None

    node_id: int = None
    parent: int = None
    childrens: List[int] = None

    def __str__(self):
        return f'role: {self.role}, action: {self.action}, state: {self.state}, content: {self.content}, input: {self.input}, output: {self.output}, parent: {self.parent}'
    
    def __repr__(self):
        return str(self)
    
    def __post_init__(self):
        assert self.role in ['user', 'system', 'root'], self.role   # root 是虚拟根节点
        assert self.action in ['root', 'input', 'output', 'plan', 'answer', 'write_code', 'run_code'], self.action
        assert self.state in ['ready', 'working', 'success', 'fail'], self.state
        self.childrens = self.childrens if self.childrens else []

    def start_work(self):
        self.state = 'working'

    def success_work(self):
        self.state = 'success'

    def fail_work(self):
        self.state = 'fail'

    def is_root(self):
        return self.role == 'root'
    
    @classmethod
    def new_root(cls):
        return cls(node_id=0, role='root', action='root', state='ready', content='', input='', output='', parent=None, childrens=[])


# 短期记忆
class Scratch:
    def __init__(self, file_path='./scratch.json'):
        self.db = TinyDB(file_path)
        nodes = [SparkNode(**node) for node in self.db.all()]
        self.spark_nodes = dict(zip([node.node_id for node in nodes], nodes))
        # 添加虚拟根节点
        if len(self.spark_nodes) == 0:
            root_node = SparkNode.new_root()
            self.spark_nodes[root_node.node_id] = root_node
            self.db.insert(root_node.__dict__)

    def new_node_id(self):
        return max(self.spark_nodes.keys()) + 1

    def node_count(self):
        return len(self.spark_nodes) - 1

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
        # 添加节点id & parent, last_node: 前面的node, node: 要添加的node
        node.node_id = self.new_node_id()
        node.parent = last_node.parent
        # 更新父节点关系
        parent = self.get_node_parent(node)
        if parent:
            parent.childrens.insert(parent.childrens.index(last_node.node_id)+1, node.node_id)
            self.update_node(parent)
        # 保存自己: 数据库 + 内存
        self.db.insert(node.__dict__)
        self.spark_nodes[node.node_id] = node
        return node
    
    def add_node_in(self, parent_node, node):
        # 添加节点id & parent
        node.node_id = self.new_node_id()
        node.parent = parent_node.node_id
        # 更新父节点关系
        parent_node.childrens.append(node.node_id)
        self.update_node(parent_node)
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
    
    def get_node_parent(self, node):
        if node.parent is None:
            return None
        else:
            return self.get_node(node.parent)
    
    def update_node(self, node):
        self.db.update(node.__dict__, Query().node_id == node.node_id)
    
    def get_node_enviroment(self, node):
        # 获取节点环境，返回节点上左右下的节点描述(string)
        lines = []
        parent = self.get_node_parent(node)
        if parent:
            if not parent.is_root():
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
    
    def success_node(self, node):
        # 节点自己完成
        node.success_work()
        self.update_node(node)
        # check父节点是否需要完成
        parent = self.get_node_parent(node)
        if parent:
            if all([self.get_node(node_id).state == 'success' for node_id in parent.childrens]):
                self.success_node(parent)

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
        if node.state in ['ready', 'working']:
            for node_id in node.childrens:
                child_todo_node = self.get_todo_node(self.get_node(node_id))
                if child_todo_node is not None:
                    return child_todo_node
            if node.is_root():
                return None
            return node
        else:
            return None
        
    def update_plans(self, current_node, posistion, new_plans):
        if posistion == 'inner':
            # 删除原有的子节点
            childrens = [self.get_node(node_id) for node_id in current_node.childrens]
            for children in childrens:
                self.delete_node(children, update_parent=False)
            # 添加新的子节点
            for new_plan in new_plans:
                new_node = SparkNode(**new_plan)
                self.add_node_in(current_node, new_node)
            # 自己状态切换成为working
            self.start_todo_node(current_node)
            return True
        
        if posistion == 'after':
            parent = self.get_node_parent(current_node)

            if parent:
                brothers = [self.get_node(node_id) for node_id in parent.childrens]
                right_brothers = brothers[brothers.index(current_node)+1:]
                # 删除节点后续所有节点
                for right_brother in right_brothers:
                    self.delete_node(right_brother, update_parent=False)
                    parent.childrens.remove(right_brother.node_id)
                # 更新父节点
                self.update_node(parent)
                # 添加新的子节点
                for new_plan in new_plans:
                    new_node = SparkNode(**new_plan)
                    self.add_node_after(current_node, new_node)
                # 完成自己
                self.success_node(current_node)
                return True
            else:
                print('fail: update_plans, position is after, but parent is None')
                return False
        print(f'Warning: update_plans not implement. position {posistion} not in [inner, after]')
        return False
