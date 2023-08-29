# 测试Memory
from base_setting import *
from GeneralAgent.memory import Memory, get_memory_importance_score, normalize

def test_get_memory_importance_score():
    rating = get_memory_importance_score('buying groceries at The Willows Market and Pharmacy')
    assert rating <= 3
    rating = get_memory_importance_score('buy a house')
    assert rating >= 8
    rating = get_memory_importance_score('I want to quit my job and start a business')
    assert rating >= 8

def test_normalize():
    arr = [1, 2, 3, 4, 5]
    normal = normalize(arr, 0, 1)
    # print(normal)
    assert normal == [0.0, 0.25, 0.5, 0.75, 1.0]

memory_path = './memory.json'

def test_memory_create():
    if os.path.exists(memory_path): os.remove(memory_path)
    memory = Memory(memory_path)
    memory.add_concept('action', '今天早上7点起床了')
    memory.add_concept('action', '早饭吃了一个包子，一碗粥')
    memory.add_concept('action', '9点到公司，开始工作')
    memory.add_concept('action', '中午吃的汉堡')
    lines = [500, 600, 700, 800, 900, 1000] * 4
    for index in range(20):
        lang = ['python', 'javascript'][index % 2]
        line_count = lines[index]
        memory.add_concept('action', f'今天工作量有点大，写了{line_count}行{lang}代码')
    # 检查反思
    thought_nodes = memory.get_concepts_with_type('thought')
    print(thought_nodes)

def test_memory_retrieve():
    memory = Memory(memory_path)
    nodes = memory.retrieve('今天吃了啥？', n_count=3)
    assert '吃' in nodes[0].concept
    assert '吃' in nodes[1].concept
    assert '吃' not in nodes[2].concept
    assert nodes[0].concept != nodes[1].concept




if __name__ == '__main__':
    # test_get_memory_importance_score()
    # test_normalize()
    test_memory_create()
    # test_memory_retrieve()