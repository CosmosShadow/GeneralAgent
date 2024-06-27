# read the document and can retrieve the information
import re
from .interpreter import Interpreter
from GeneralAgent.memory import LinkMemory


class LinkRetrieveInterperter(Interpreter):
    """
    """

    def __init__(self, python_interpreter=None, sparks_dict_name='sparks'):
        self.python_intrepreter = python_interpreter
        self.sparks_dict_name = sparks_dict_name
        self.link_memory = LinkMemory()

    def prompt(self, messages) -> str:
        if self.link_memory.is_empty():
            return ''
        else:
            access_prompt = f"""
In Python, You can access the values of <<key>> in all documents through the dictionary {self.sparks_dict_name}, such as <<Hello world>>:
```python
self.sparks_dict_name['Hello world']
```
"""
            info = self.link_memory.get_memory(messages)
            # return 'Background Information: \n' + info + access_prompt
            return 'Background Information: \n' + info