from base_setting import *
from GeneralAgent.interpreter import ShellInterpreter, AppleScriptInterpreter, PythonInterpreter
from GeneralAgent.interpreter import FileInterpreter, PlanInterpreter, AskInterpreter
from GeneralAgent.memory import Memory, MemoryNode

def test_file_interpreter():
    interpreter = FileInterpreter()
    target_path = './data/a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    
    # write
    write_content = """
To write the description of Chengdu to the file %s in one step, you can use the following command:

```
file %s write 0 -1 <<EOF
Chengdu is a sub-provincial city which serves as the capital of Sichuan province. It is one of the three most populous cities in Western China, the other two being Chongqing and Xi'an. As of 2021, the administrative area of Chengdu has a population of over 16 million. Chengdu is famous for its spicy Sichuan cuisine, giant pandas, and historical and cultural heritage. It is also an important transportation hub and a center for science and technology in Western China.
EOF
```

""" % (target_path, target_path)
    assert interpreter.match(write_content) is True
    output, is_stop = interpreter.parse(write_content)
    assert is_stop is False
    assert output.strip() == 'write successfully'
    assert os.path.exists(target_path)

    # read
    read_content = """
firsrt, read the file.
```
file %s read 0 -1
```
""" % (target_path, )
    assert interpreter.match(read_content) is True
    output, is_stop = interpreter.parse(read_content)
    assert is_stop is False
    assert 'Chengdu is a sub-provincial city' in output


if __name__ == '__main__':
    test_file_interpreter()