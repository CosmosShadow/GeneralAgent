# 记忆
import datetime
import tinydb   # 存储所有记忆，优点是: 实时逐步序列化，即使程序崩溃了也记录了

# 记忆节点
# 注意: 记忆节点是不可变的
class ConceptNode:
    @classmethod
    def from_dict(cls, dict):
        return cls(dict['type'], dict['concept'], dict['create_at'], dict['concept_embedding'])

    def __init__(self, type, index, concept, concept_embedding, priority, create_at=None):
        self.type = type    # input, output, thought, plan, action
        self.index = index  # 索引
        self.concept = concept  # 概念
        self.concept_embedding = concept_embedding
        self.priority = priority    # 重要性
        if create_at is None:
            create_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.create_at = create_at    # 创建时间，字符串

    def __str__(self) -> str:
        return f'[{self.type}] {self.index} {self.create_at} {self.concept}'


# 记忆
class Memory:
    def __init__(self, file_path, embedding_fun=None) -> None:
        self.embedding_fun = embedding_fun
        self.db = tinydb.TinyDB(file_path)
        self.concept_nodes = [ConceptNode.from_dict(record) for record in self.db.all()]

    def add_concept(self, type, concept, concept_embedding=None):
        # 添加概念
        if concept_embedding is None:
            concept_embedding = self.embedding_fun(concept)
        # TODO: 计算优先级
        priority = 0
        concept_node = ConceptNode(type, len(self.concept_nodes), concept, concept_embedding=concept_embedding, priority=priority)
        self.concept_nodes.append(concept_node)
        self.insert(concept_node)

        # TODO: 触发反思

        return concept_node

    def get_concept_with_type(self, type):
        # 获取某种类型的概念
        return [concept_node for concept_node in self.concept_nodes if concept_node.type == type]
    
    def retrieve(self, focus_points):
        # 检索, focus_points 是关注的点，字符串数组
        pass