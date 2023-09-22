from base_setting import *
from GeneralAgent.interpreter import CodeInterpreter
import os

init_code = """
import os
import sys
sys.path.append('../')
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools
from GeneralAgent.llm import prompt_call
"""

def test_CodeInterpreter():
    serialize_path = './test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    # 基础
    interpreter = CodeInterpreter(serialize_path, init_code)
    success, sys_stdout = interpreter.run_code('hello world', 'print("hello world")')
    # print(success, sys_stdout)

    # 表达式
    interpreter.set_variable('a', 10)
    success, sys_stdout = interpreter.run_code('add self', 'a += 1')
    a = interpreter.get_variable('a')
    assert a == 11

    # 工具: 爬取网页
    code = """
url = 'https://tongtianta.ai'
soup = scrape_web(url)
title = soup.title.string
"""
    success, sys_stdout = interpreter.run_code('scrape web', code)
    # print(sys_stdout)
    assert success
    title = interpreter.get_variable('title')
    assert title == '通天塔AI'

    # 工具: 大模型
    code = """
prompt = "你是一个翻译官，将下面```包围起来的的文本翻译成为{{target}}: \\n```\\n{{text}}\\n```\\n"
variables = {'target': 'chinese', 'text': 'I love china'}
json_schema = \"\"\" {"source": "{text to translate}","translated": "{the translated text}"} \"\"\"
result = prompt_call(prompt, variables, json_schema)
"""
    # print(code)
    success, sys_stdout = interpreter.run_code('prompt call', code)
    assert success
    result = interpreter.get_variable('result')
    # print(result)
    assert result['source'] == 'I love china'
    assert result['translated'] == '我爱中国'

    
    if os.path.exists(serialize_path): os.remove(serialize_path)



if __name__ == '__main__':
    test_CodeInterpreter()