from base_setting import *
from GeneralAgent.code import CodeWorkspace
import os

init_code = """
import os
import sys
# 添加项目根目录到环境变量
sys.path.append('../')
# 加载项目配置文件
import dotenv
dotenv.load_dotenv('../GeneralAgent/.env')
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools
"""

def test_CodeWorkspace():
    serialize_path = './test_code_workspace.pkl'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    code_workspace = CodeWorkspace(serialize_path, init_code)
    success, sys_stdout = code_workspace.run_code('hello world', 'print("hello world")')
    # print(success, sys_stdout)

    code_workspace.set_variable('a', 10)
    success, sys_stdout = code_workspace.run_code('add self', 'a += 1')
    a = code_workspace.get_variable('a')
    assert a == 11

    code = """
url = 'https://tongtianta.ai'
title, text, links = scrape_web(url)
"""
    success, sys_stdout = code_workspace.run_code('scrape web', code)
    assert success
    title = code_workspace.get_variable('title')
    assert title == '通天塔AI'
    
    if os.path.exists(serialize_path): os.remove(serialize_path)



if __name__ == '__main__':
    test_CodeWorkspace()