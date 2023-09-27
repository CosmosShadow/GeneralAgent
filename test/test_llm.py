# 测试llm
from base_setting import *
from GeneralAgent.llm import embedding_fun, cos_sim, llm_inference

def test_embedding_fun():
    texts = [
        "我爱唱歌",
        "I love singing"
    ]
    embeddings = [embedding_fun(text) for text in texts]
    a, b = embeddings[0], embeddings[1]
    assert cos_sim(a, a) >= 0.999
    assert cos_sim(a, b) > 0.8

def test_llm_inference():
    messages = [
        {'role': 'system', 'content': 'you are a helpful assistant'},
        {'role': 'user', 'content': '1 + 1 = ?'},
    ]
    result = ''
    for x in llm_inference(messages):
        if x is None:
            break
        result += x
    assert '2' in result

def test_llm_inference_break():
    messages = [
        {'role': 'system', 'content': 'you are a helpful assistant'},
        {'role': 'user', 'content': 'describle the Chengdu'},
    ]
    result = ''
    for x in llm_inference(messages):
        if x is None:
            break
        # print(x, end='', flush=True)
        result += x
        if len(result) > 10:
            break
    assert len(result) > 10

    result = ''
    for x in llm_inference(messages):
        result += x
        if len(result) > 10:
            break
    assert len(result) > 10


if __name__ == '__main__':
    test_embedding_fun()
    test_llm_inference()
    test_llm_inference_break()