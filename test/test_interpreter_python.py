import os
from GeneralAgent.interpreter import PythonInterpreter


def test_python_interpreter():
    # test run
    serialize_path = "test/data/test_interpreter.bin"
    if os.path.exists(serialize_path):
        os.remove(serialize_path)

    interpreter = PythonInterpreter(serialize_path=serialize_path)
    result, is_stop = interpreter.output_parse(
        '```python\n#run code\n"hello world"\n```'
    )
    print(result)
    assert "hello world" in result.strip()
    # assert is_stop is False

    # test aug assignment
    interpreter.set_variable("a", 10)
    result, is_stop = interpreter.output_parse("```python\n#run code\na += 1\n```")
    a = interpreter.get_variable("a")
    assert a == 11

    result, is_stop = interpreter.output_parse("```python\n#run code\na += 1\n```")
    a = interpreter.get_variable("a")
    assert a == 12

    # test ann assignment
    result, is_stop = interpreter.output_parse("```python\n#run code\na: int = 1\n```")
    a = interpreter.get_variable("a")
    assert a == 1

    # test normal assignment
    result, is_stop = interpreter.output_parse("```python\n#run code\nb = 1\n```")
    b = interpreter.get_variable("b")
    assert b == 1

    # test multiline code
    result, is_stop = interpreter.output_parse(
        "```python\n#run code\n[\n    1,\n    2,\n    3\n]\n```"
    )
    assert "[1, 2, 3]" == result.split("\n")[-2]

    # test multiple assignment
    result, is_stop = interpreter.output_parse("```python\n#run code\na, b = 1, 2\n```")
    a = interpreter.get_variable("a")
    b = interpreter.get_variable("b")
    assert a == 1
    assert b == 2
    assert "(1, 2)" == result.split("\n")[-2]


def test_stack_code():
    serialize_path = "test/data/test_interpreter.bin"
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    interpreter = PythonInterpreter(serialize_path=serialize_path)
    code = """
```python
#run code
a = 10
code = "```python\\na += 1\\n```"
interpreter.output_parse(code)
a
```
"""
    interpreter.set_variable("interpreter", interpreter)
    result, is_stop = interpreter.output_parse(code)
    # print(result)
    assert "11" in result.strip()


# output:
# 11
# python runs result:
# run successfully


def test_run_code():
    code = """
def test():
    return "hello world"
test()
"""
    interpreter = PythonInterpreter()
    result, is_stop = interpreter.run_code(code)
    # print(result)
    assert "hello world" in result.strip()
