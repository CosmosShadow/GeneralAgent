# 测试llm
from base_setting import *
from GeneralAgent.llm import cache_translate_eng

def test_cache_translate_eng():
    text = "你是一个翻译官，将下面的文本翻译成为{{target}}: {{text}}"
    en = cache_translate_eng(text)
    print(en)
    assert "{{target}}" in en
    assert "{{text}}" in en

if __name__ == '__main__':
    test_cache_translate_eng()