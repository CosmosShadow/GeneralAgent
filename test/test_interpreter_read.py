import shutil
from GeneralAgent.interpreter import EmbeddingRetrieveInterperter



def test_read_interpreter():
    import os
    workspace = './data/read_interpreter/'
    content = """
```read
./data/Nougat_piece.pdf
```
"""
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    
    interpreter = EmbeddingRetrieveInterperter(serialize_path=workspace)
    interpreter.input_parse(content)

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
