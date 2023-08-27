# 测试llm
from base_setting import *
from GeneralAgent.llm import cache_translate_eng, embedding_fun, cos_sim

def test_cache_translate_eng():
    text = "你是一个翻译官，将下面的文本翻译成为{{target}}: {{text}}"
    en = cache_translate_eng(text)
    print(en)
    assert "{{target}}" in en
    assert "{{text}}" in en

def test_embedding_fun():
    texts = [
        "我爱中国",
        "I love china"
    ]
    embeddings = embedding_fun(texts)
    a, b = embeddings[0], embeddings[1]
    assert cos_sim(a, a) >= 0.999
    assert cos_sim(a, b) > 0.9


if __name__ == '__main__':
    # test_cache_translate_eng()
    test_embedding_fun()