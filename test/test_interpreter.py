from base_setting import *
from GeneralAgent.interpreter import CodeInterpreter, add_print

def test_add_print():
    code = """
a = 1
a
    c
try:
"""
    code = add_print(code)
    assert code == """
a = 1
print(a)
    print(c)
try:
"""

def test_CodeInterpreter():
    serialize_path = './test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = CodeInterpreter(serialize_path)
    success, sys_stdout = interpreter.run_code('print("hello world")')
    assert sys_stdout.strip() == 'hello world'

    interpreter.set_variable('a', 10)
    success, sys_stdout = interpreter.run_code('a += 1')
    a = interpreter.get_variable('a')
    assert a == 11

    success, sys_stdout = interpreter.run_code('a += 1')
    a = interpreter.get_variable('a')
    assert a == 21

    code = """
url = 'https://tongtianta.ai'
result = scrape_web(url)
title = result[0]
"""
    success, sys_stdout = interpreter.run_code(code)
    assert success
    title = interpreter.get_variable('title')
    assert title == '通天塔AI'


if __name__ == '__main__':
    # test_add_print()
    test_CodeInterpreter()