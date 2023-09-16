# 测试llm
from base_setting import *
from GeneralAgent.llm import translate_eng, embedding_fun, cos_sim, prompt_call, is_english

def test_is_english():
    text = """On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.
Memory: {{concept}}
Rating: <fill in>
"""
    assert is_english(text)
    assert not is_english(text + '中国')

def test_translate_eng():
    text = "你是一个翻译官，将下面的文本翻译成为{{target}}: {{text}}"
    en = translate_eng(text)
    print(en)
    assert "{{target}}" in en
    assert "{{text}}" in en

def test_embedding_fun():
    texts = [
        "我爱中国",
        "I love china"
    ]
    embeddings = [embedding_fun(text) for text in texts]
    a, b = embeddings[0], embeddings[1]
    assert cos_sim(a, a) >= 0.999
    assert cos_sim(a, b) > 0.9

def test_prompt_call():
    prompt = "你是一个翻译官，将下面```包围起来的的文本翻译成为{{target}}: \n```\n{{text}}\n```\n"
    variables = {'target': 'chinese', 'text': 'I love china'}
    json_schema = """ {"source": "{text to translate}","translated": "{the translated text}"} """
    result = prompt_call(prompt, variables, json_schema)
    assert result['source'] == 'I love china'
    assert result['translated'] == '我爱中国'


if __name__ == '__main__':
    test_is_english()
    test_translate_eng()
    test_embedding_fun()
    test_prompt_call()