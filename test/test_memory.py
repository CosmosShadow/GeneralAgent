# 测试Memory
from base_setting import *
from GeneralAgent.memory import Memory, get_memory_importance_score, normalize
from GeneralAgent.memory import generate_questions_by_statements, get_insights_and_evidence

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

statement_list = [
    "今天早上7点起床了",
    "9点到公司，开始工作",
    "早饭吃了一个包子，一碗粥",
    "今天工作量有点大，写了700行python代码",
    "今天工作量有点大，写了1000行javascript代码",
    "今天工作量有点大，写了700行python代码",
    "今天工作量有点大，写了1000行javascript代码",
    "今天工作量有点大，写了700行python代码",
    "今天工作量有点大，写了1000行javascript代码",
    "今天工作量有点大，写了500行python代码",
    "今天工作量有点大，写了500行python代码",
    "今天工作量有点大，写了500行python代码",
    "今天工作量有点大，写了500行python代码",
    "今天工作量有点大，写了600行javascript代码",
    "今天工作量有点大，写了600行javascript代码",
    "今天工作量有点大，写了600行javascript代码",
    "今天工作量有点大，写了800行javascript代码",
    "今天工作量有点大，写了800行javascript代码",
    "今天工作量有点大，写了800行javascript代码",
    "今天工作量有点大，写了900行python代码",
    "今天工作量有点大，写了900行python代码",
    "今天工作量有点大，写了900行python代码"
]

def test_generate_questions_by_statements():
    global statement_list
    questions = generate_questions_by_statements(statement_list)
    print(questions)
    assert len(questions) <= 2

def test_get_insights_and_evidence():
    global statement_list
    questions = ['今天一共写了多少行python代码和javascript代码？', '对于如此高的工作量，你觉得自己的工作压力大吗？']
    for q in questions:
        insights = get_insights_and_evidence(statement_list, topic=q)
        print(insights)

memory_path = './memory.json'

def test_memory_create_and_retrieve():
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
    print('thought_nodes:')
    for node in thought_nodes:
        print(node.concept)

    # 预期输出:
    # thought_nodes:
    # The speaker wrote a large amount of code today, with both Python and Javascript code written
    # The speaker started work at 9AM and had specific meals throughout the day
    # The speaker uses both Python and Javascript in their work, but they write more lines of Python code than Javascript
    # The speaker's work involves substantial coding, requiring them to write thousands of lines of code within a day

    # 检索
    memory = Memory(memory_path)
    nodes = memory.retrieve('今天吃了啥？', n_count=3)
    assert '吃' in nodes[0].concept
    assert '吃' in nodes[1].concept
    assert '吃' not in nodes[2].concept
    assert nodes[0].concept != nodes[1].concept

    if os.path.exists(memory_path): os.remove(memory_path)




if __name__ == '__main__':
    # test_get_memory_importance_score()
    # test_normalize()
    test_memory_create()
    # test_memory_retrieve()
    # test_generate_questions_by_statements()
    # test_get_insights_and_evidence()