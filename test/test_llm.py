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
    result = llm_inference(messages)
    assert '2' in result


if __name__ == '__main__':
    test_embedding_fun()
    test_llm_inference()