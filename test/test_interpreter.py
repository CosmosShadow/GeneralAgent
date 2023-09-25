from base_setting import *
from GeneralAgent.interpreter import PythonInterpreter
from GeneralAgent.interpreter import BashInterperter


def test_python_interpreter():
    # test add print
    code = """
a = 1
a
    c
try:
"""
    code = PythonInterpreter.add_print(code)
    assert code == """
a = 1
print(a)
    print(c)
try:
"""
    # test run
    serialize_path = './test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = PythonInterpreter(serialize_path)
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


def test_bash_interperter():
    interpreter = BashInterperter()
    result, sys_out = interpreter.parse("""```runbash\npython ./data/hello.py\n```""")
    # print(result)
    # print(sys_out)
    assert 'hello world' in sys_out


if __name__ == '__main__':
    # test_add_print()
    # test_python_interpreter()
    test_bash_interperter()