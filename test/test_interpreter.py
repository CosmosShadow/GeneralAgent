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
    sys_stdout = interpreter.run_code('print("hello world")')
    assert sys_stdout.strip() == 'hello world'

    interpreter.set_variable('a', 10)
    sys_stdout = interpreter.run_code('a += 1')
    a = interpreter.get_variable('a')
    assert a == 11

    sys_stdout = interpreter.run_code('a += 1')
    a = interpreter.get_variable('a')
    assert a == 12

    code = """
url = 'https://tongtianta.ai'
result = scrape_web(url)
title = result[0]
"""
    sys_stdout = interpreter.run_code(code)
    title = interpreter.get_variable('title')
    assert title == '通天塔AI'


def test_bash_interperter():
    interpreter = BashInterperter()
    output, is_stop = interpreter.parse("""```shell\npython ./data/hello.py\n```""")
    assert 'hello world' in output
    assert is_stop is False


if __name__ == '__main__':
    test_python_interpreter()
    test_bash_interperter()