# 记忆
import datetime
# 存储所有记忆，优点是: 实时逐步序列化，即使程序崩溃了也记录了
from tinydb import TinyDB, Query
from GeneralAgent.llm import prompt_call, cos_sim, embedding_fun

ConceptNodeTypes = ['input', 'output', 'thought', 'plan', 'action']
ConceptNodeStates = ['ready', 'done', 'cancel', 'fail'] # 状态只能从ready转移到其他三个中去

def _get_memory_importance_score(concept):
    """获取记忆的重要性评分"""
    # 在 1 到 10 的范围内，其中 1 是纯粹平凡的（例如，刷牙、整理床铺），而 10 是极其痛苦的（例如，分手、大学录取），请评估以下记忆片段可能的痛苦程度。
    # 记忆：{{概念}}
    # 评分：<填写>

    # 这段prompt需要用英文写，因为 eng -> zh -> eng 损失了很多意思，评分不准
    prompt = """On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.\nMemory: {{concept}}\nRating: <fill in>"""

    json_schema = '{"rating": the_integer_score}'
    try:
        result = prompt_call(prompt, {'concept': concept}, json_schema)
        return int(result['rating'])
    except:
        return None
    
def get_memory_importance_score(concept):
    for _ in range(2):
        priority = _get_memory_importance_score(concept)
        if priority is not None:
            return priority
    print('Warning: get_memory_importance_score failed multi times, set priority to 5')
    return 5

str2date = lambda x: datetime.datetime.now() if (x is None) else datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
date2str = lambda x: x.strftime('%Y-%m-%d %H:%M:%S')

# 记忆节点
class ConceptNode:
    @classmethod
    def from_dict(cls, dict):
        return cls(dict['type'], dict['index'], dict['concept'], dict['priority'], dict['create_at'], dict['last_access'], dict['state'], dict['from_nodes'], dict['to_nodes'])

    def __init__(self, type, index, concept, priority, create_at=None, last_access=None, state='done', from_nodes=[], to_nodes=[]):
        # 验证
        assert type in ConceptNodeTypes
        assert state in ConceptNodeStates
        if type == 'plan':
            assert concept.startswith('[plan]') or concept.startswith('[action]') or concept.startswith('[response]')
        # 赋值
        self.type = type    # string: input, output, thought, plan, action
        self.index = index  # 索引 int
        self.concept = concept  # 概念 string
        self.concept_embedding = embedding_fun(concept) # 概念embedding ([float])
        self.priority = priority    # 重要性 (float: 0~10)
        self.create_at = str2date(create_at) # 创建时间, string
        self.last_access = str2date(last_access) # 最新访问时间, string。最近再次访问过，容易被提取
        self.state = state  # 状态 string: ready、done、cancel
        self.from_nodes = from_nodes        # 来源 [index]
        self.to_nodes = to_nodes        # 被引用 -> 一般都是计划实行情况 [index]

    def __str__(self) -> str:
        return f'[{self.type}] {self.index} {self.state} {self.create_at} {self.concept}'
    
    def to_save_dict(self):
        value_dict = self.__dict__.copy()
        value_dict['create_at'] = date2str(value_dict['create_at'])
        value_dict['last_access'] = date2str(value_dict['last_access'])
        value_dict.pop('concept_embedding')
        return value_dict

# 记忆
class Memory:
    def __init__(self, file_path='./memory.json') -> None:
        # file_path: 存储路径，比如 xxx.json
        self.db = TinyDB(file_path)
        self.concept_nodes = [ConceptNode.from_dict(record) for record in self.db.all()]

    def add_concept(self, type, concept):
        assert type in ConceptNodeTypes
        
        # 计算优先级(重要性)
        priority = get_memory_importance_score(concept)
        
        concept_node = ConceptNode(type, len(self.concept_nodes), concept, priority=priority)
        self.concept_nodes.append(concept_node)
        
        # 保存
        self.db.insert(concept_node.to_save_dict())

        # TODO: 触发反思

        return concept_node
    
    def update_concept(self, concept_node: ConceptNode):
        # 更新概念节点
        concept_node.last_access = datetime.datetime.now()
        self.db.update(concept_node.to_save_dict(), Query().index == concept_node.index)

    def new_access(self, concept_node: ConceptNode):
        # 更新最新访问时间
        concept_node.last_access = datetime.datetime.now()
        self.db.update(concept_node.to_save_dict(), Query().index == concept_node.index)

    def get_concept_with_type(self, type):
        # 获取某种类型的概念
        return [concept_node for concept_node in self.concept_nodes if concept_node.type == type]
    
    def get_plan_in_plan(self):
        # 获取计划中的计划
        return [x for x in self.concept_nodes if x.type == 'plan' and x.concept.startswith('[plan]')]
    
    def retrieve(self, focus_point, n_count=30):
        # 根据关注点(focus_point, string)，获取前n_count个相关记忆内容
        focal_embedding = embedding_fun(focus_point)
        # 按时间排序记忆节点
        nodes = list(sorted(self.concept_nodes, key=lambda x: x.create_at))
        # 计算因子
        recency = [0.99 ** index for index in range(1, len(nodes) + 1)]
        importance = [node.priority for node in nodes]
        relevance = [cos_sim(node.concept_embedding, focal_embedding) for node in nodes]
        # 正则化
        recency = normalize(recency, 0, 1)
        importance = normalize(importance, 0, 1)
        relevance = normalize(relevance, 0, 1)
        # 排序因子 = recency * 0.5 + relevance * 3 + importance * 2
        score = [recency[i]*0.5 + relevance[i]*3 + importance[i]*2 for i in range(len(nodes))]
        # 获取score前n_count个最大值，且以对应的大小来排序了
        top_n_index = sorted(range(len(score)), key=lambda i: score[i], reverse=True)[:n_count]
        master_nodes = [nodes[index] for index in top_n_index]
        # 更新最新访问时间
        for node in master_nodes:
            self.new_access(node)
        return master_nodes


def retrieve(persona, perceived): 
  """
  This function takes the events that are perceived by the persona as input
  and returns a set of related events and thoughts that the persona would 
  need to consider as context when planning. 

  INPUT: 
    perceived: a list of event <ConceptNode>s that represent any of the events
    `         that are happening around the persona. What is included in here
              are controlled by the att_bandwidth and retention 
              hyper-parameters.
  OUTPUT: 
    retrieved: a dictionary of dictionary. The first layer specifies an event, 
               while the latter layer specifies the "curr_event", "events", 
               and "thoughts" that are relevant.
  """
  # We rerieve events and thoughts separately. 
  retrieved = dict()
  for event in perceived: 
    retrieved[event.description] = dict()
    retrieved[event.description]["curr_event"] = event
    
    relevant_events = persona.a_mem.retrieve_relevant_events(
                        event.subject, event.predicate, event.object)
    retrieved[event.description]["events"] = list(relevant_events)

    relevant_thoughts = persona.a_mem.retrieve_relevant_thoughts(
                          event.subject, event.predicate, event.object)
    retrieved[event.description]["thoughts"] = list(relevant_thoughts)
    
  return retrieved


def normalize(arr, target_min, target_max):
    assert target_max > target_min
    min_val = min(arr)
    max_val = max(arr)
    range_val = max_val - min_val
    normal = lambda x: ((x - min_val) * (target_max - target_min) / range_val + target_min)
    if range_val == 0: 
        return [(target_max - target_min)/2] * len(arr)
    else: 
        return [normal(x) for x in arr]