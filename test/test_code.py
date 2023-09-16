from base_setting import *
from GeneralAgent.code_workspace import CodeWorkspace
import os

init_code = """
import os
import sys
sys.path.append('../')
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools
from GeneralAgent.llm import prompt_call
"""

def test_CodeWorkspace():
    serialize_path = './test_code_workspace.pkl'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    # 基础
    code_workspace = CodeWorkspace(serialize_path, init_code)
    success, sys_stdout = code_workspace.run_code('hello world', 'print("hello world")')
    # print(success, sys_stdout)

    # 表达式
    code_workspace.set_variable('a', 10)
    success, sys_stdout = code_workspace.run_code('add self', 'a += 1')
    a = code_workspace.get_variable('a')
    assert a == 11

    # 工具: 爬取网页
    code = """
url = 'https://tongtianta.ai'
soup = scrape_web(url)
title = soup.title.string
"""
    success, sys_stdout = code_workspace.run_code('scrape web', code)
    # print(sys_stdout)
    assert success
    title = code_workspace.get_variable('title')
    assert title == '通天塔AI'

    # 工具: 大模型
    code = """
prompt = "你是一个翻译官，将下面```包围起来的的文本翻译成为{{target}}: \\n```\\n{{text}}\\n```\\n"
variables = {'target': 'chinese', 'text': 'I love china'}
json_schema = \"\"\" {"source": "{text to translate}","translated": "{the translated text}"} \"\"\"
result = prompt_call(prompt, variables, json_schema)
"""
    # print(code)
    success, sys_stdout = code_workspace.run_code('prompt call', code)
    assert success
    result = code_workspace.get_variable('result')
    # print(result)
    assert result['source'] == 'I love china'
    assert result['translated'] == '我爱中国'

    
    if os.path.exists(serialize_path): os.remove(serialize_path)



if __name__ == '__main__':
    test_CodeWorkspace()