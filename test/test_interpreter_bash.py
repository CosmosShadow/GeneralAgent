
from GeneralAgent.interpreter import ShellInterpreter

def test_bash_interperter():
    interpreter = ShellInterpreter()
    output, is_stop = interpreter.output_parse("""```shell\npython ./data/hello.py\n```""")
    assert 'hello world' in output
    assert is_stop is False

if __name__ == '__main__':
    test_bash_interperter()