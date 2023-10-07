from base_setting import *
import shutil
from GeneralAgent.interpreter import RetrieveInterpreter

content = """
```read
./data/Nougat_piece.pdf
```
"""

def test_read_interpreter():
    workspace = './data/read_interpreter/'
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    
    interpreter = RetrieveInterpreter(serialize_path=workspace)
    interpreter.parse(content)

    messages = [
        {'role': 'system', 'content': 'what is the advantage of the Model?'}
    ]
    prompt = interpreter.prompt(messages)
    # print(prompt)
    assert len(prompt) > 0

    if os.path.exists(workspace):
        shutil.rmtree(workspace)


if __name__ == '__main__':
    test_read_interpreter()
