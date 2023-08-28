# 记忆
import datetime
# 存储所有记忆，优点是: 实时逐步序列化，即使程序崩溃了也记录了
from tinydb import TinyDB, Query
from GeneralAgent.llm import prompt_call, cos_sim, embedding_fun

ConceptNodeTypes = ['input', 'output', 'thought', 'plan', 'action']
ConceptNodeStates = ['ready', 'done', 'cancel', 'fail'] # 状态只能从ready转移到其他三个中去

def get_memory_importance_score(concept):
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


# 记忆节点
class ConceptNode:
    @classmethod
    def from_dict(cls, dict):
        return cls(dict['type'], dict['concept'], dict['create_at'], dict['concept_embedding'], dict['priority'], dict['create_at'], dict['state'], dict['from_nodes'], dict['to_nodes'])

    def __init__(self, type, index, concept, concept_embedding, priority, create_at=None, last_access=None, state='done', from_nodes=[], to_nodes=[]):
        # 验证
        assert type in ConceptNodeTypes
        assert state in ConceptNodeStates
        if type == 'plan':
            assert concept.startswith('[plan]') or concept.startswith('[action]') or concept.startswith('[response]')
        # 赋值
        self.type = type    # string: input, output, thought, plan, action
        self.index = index  # 索引 int
        self.concept = concept  # 概念 string
        self.concept_embedding = concept_embedding # 概念embedding ([float])
        self.priority = priority    # 重要性 (float: 0~10)
        self.create_at = create_at or datetime.datetime.now() # 创建时间, string
        self.last_access = last_access or datetime.datetime.now() # 最新访问时间, string。最近再次访问过，容易被提取
        self.state = state  # 状态 string: ready、done、cancel
        self.from_nodes = from_nodes        # 来源 [index]
        self.to_nodes = to_nodes        # 被引用 -> 一般都是计划实行情况 [index]

    def __str__(self) -> str:
        return f'[{self.type}] {self.index} {self.state} {self.create_at} {self.concept}'
    
    def to_save_dict(self):
        value_dict = self.__dict__.deepcoy()
        value_dict['create_at'] = value_dict['create_at'].strftime('%Y-%m-%d %H:%M:%S')
        value_dict['last_access'] = value_dict['last_access'].strftime('%Y-%m-%d %H:%M:%S')


# 记忆
class Memory:
    def __init__(self, file_path, embedding_fun=None) -> None:
        # file_path: 存储路径，比如 xxx.json
        # embedding_fun: 用于计算概念的embedding
        self.embedding_fun = embedding_fun
        self.db = TinyDB(file_path)
        self.concept_nodes = [ConceptNode.from_dict(record) for record in self.db.all()]

    def add_concept(self, type, concept, concept_embedding=None):
        if concept_embedding is None:
            concept_embedding = self.embedding_fun(concept)
        
        # 计算优先级(重要性)
        priority = get_memory_importance_score(concept)
        if priority is None:
            priority = get_memory_importance_score(concept) or 5
        
        concept_node = ConceptNode(type, len(self.concept_nodes), concept, concept_embedding=concept_embedding, priority=priority)
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
    
    def retrieve(self, focus_points, top_k):
        # 检索, focus_points 是关注的点
        # TODO: 检索
        pass


from numpy import dot
from numpy.linalg import norm

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



def normalize_dict_floats(d, target_min, target_max):
  """
  This function normalizes the float values of a given dictionary 'd' between 
  a target minimum and maximum value. The normalization is done by scaling the
  values to the target range while maintaining the same relative proportions 
  between the original values.
  INPUT: 
    d: Dictionary. The input dictionary whose float values need to be 
       normalized.
  """
  min_val = min(val for val in d.values())
  max_val = max(val for val in d.values())
  range_val = max_val - min_val

  if range_val == 0: 
    for key, val in d.items(): 
      d[key] = (target_max - target_min)/2
  else: 
    for key, val in d.items():
      d[key] = ((val - min_val) * (target_max - target_min) 
                / range_val + target_min)
  return d


def top_highest_x_values(d, x):
    """returns a new dictionary containing the top 'x' key-value pairs from the input dictionary 'd' with the highest values."""
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True)[:x])
  

def extract_recency(nodes: [ConceptNode]):
    recency_vals = [0.99 ** i for i in range(1, len(nodes) + 1)]
    recency_out = dict()
    for index, node in enumerate(nodes): 
        recency_out[node.index] = recency_vals[index]
    return recency_out

def extract_importance(nodes):
    importance_out = dict()
    for index, node in enumerate(nodes): 
        importance_out[node.index] = node.poignancy
    return importance_out

def extract_relevance(nodes, focal_pt):
    focal_embedding = embedding_fun(focal_pt)
    relevance_out = dict()
    for count, node in enumerate(nodes): 
        relevance_out[node.index] = cos_sim(node.concept_embedding, focal_embedding)
    return relevance_out


def new_retrieve(memory, focal_point, n_count=30):
    # 按时间排序记忆节点
    nodes = list(sorted(memory.concept_nodes, key=lambda x: x.create_at))
    # 排序因子 = recency * 0.5 + relevance * 3 + importance * 2
    recency_out = extract_recency(nodes)
    recency_out = normalize_dict_floats(recency_out, 0, 1)
    importance_out = extract_importance(nodes)
    importance_out = normalize_dict_floats(importance_out, 0, 1)  
    relevance_out = extract_relevance(nodes, focal_point)
    relevance_out = normalize_dict_floats(relevance_out, 0, 1)

    gw = [0.5, 3, 2]
    master_out = dict()
    for key in recency_out.keys(): 
        master_out[key] = (recency_out[key]*gw[0] + relevance_out[key]*gw[1] + importance_out[key]*gw[2])

    master_out = top_highest_x_values(master_out, len(master_out.keys()))

    master_out = top_highest_x_values(master_out, n_count)
    master_nodes = [memory.concept_nodes[index] for index in list(master_out.keys())]

    for node in master_nodes:
        memory.new_access(node)

    return master_nodes