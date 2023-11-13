# read the document and can retrieve the information
import re
from .interpreter import Interpreter
from GeneralAgent.memory import LinkMemory


class LinkRetrieveInterperter(Interpreter):
    """
    LinkRetrieveInterperter store and retrieve the information from the memory by link embed in the document. like I live in <<My Home>>.
    """
    
    match_pattern = '```read\n(.*?)\n```'

    def __init__(self, python_interpreter=None, sparks_dict_name='sparks'):
        self.python_intrepreter = python_interpreter
        self.sparks_dict_name = sparks_dict_name
        self.link_memory = LinkMemory()

    def get_python_access_prompt(self):
        variable_name = self.sparks_dict_name
        return f"""
You can access the values of <<key>> in all documents through the dictionary {variable_name}, such as <<Hello world>>:
```
print({variable_name}['Hello world'])
```
"""

    async def prompt(self, messages) -> str:
        if self.link_memory.is_empty():
            return ''
        else:
            return await self.link_memory.get_memory(messages)
    
    def update_python_variables(self):
        if self.python_intrepreter is not None:
            nodes = self.link_memory.concepts.values()
            sparks_dict = dict(zip([node.key for node in nodes], [node.content for node in nodes]))
            self.python_intrepreter.set_variable(self.sparks_dict_name, sparks_dict)
    
    async def parse(self, string):
        from GeneralAgent import skills
        pattern = re.compile(self.match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        file_paths = match.group(1).strip().split('\n')
        result = ''
        async def output_callback(token):
            nonlocal result
            if token is not None:
                result += token
        for file_path in file_paths:
            content = skills.read_file_content(file_path)
            await self.link_memory.add_memory(content, output_callback=output_callback)
        self.update_python_variables()
        return string + '\n' + result, True