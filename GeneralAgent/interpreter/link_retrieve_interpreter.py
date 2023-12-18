# read the document and can retrieve the information
import re
from .interpreter import Interpreter
from GeneralAgent.memory import LinkMemory


class LinkRetrieveInterperter(Interpreter):
    """
    LinkRetrieveInterperter store and retrieve the information from the memory by link embed in the document. like I live in <<My Home>>.
    LinkRetrieveInterperter handle input string like this:
    ```read
    path/to/file1.pdf
    path/to/file2.pdf
    ```
    """
    
    input_match_pattern = '```read\n(.*?)\n```'

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
```
print({self.sparks_dict_name}['Hello world'])
```
"""
            info = self.link_memory.get_memory(messages)
            return 'Background Information: \n' + info + access_prompt
    
    def input_parse(self, string) -> (str, bool):
        from GeneralAgent import skills
        pattern = re.compile(self.input_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        file_paths = match.group(1).strip().split('\n')
        result = ''
        def output_callback(token):
            nonlocal result
            if token is not None:
                result += token
        for file_path in file_paths:
            content = skills.read_file_content(file_path)
            self.link_memory.add_memory(content, output_callback=output_callback)
        self._update_python_variables()
        return string + '\n' + result, True
    
    def _update_python_variables(self):
        if self.python_intrepreter is not None:
            nodes = self.link_memory.concepts.values()
            sparks_dict = dict(zip([node.key for node in nodes], [node.content for node in nodes]))
            self.python_intrepreter.set_variable(self.sparks_dict_name, sparks_dict)