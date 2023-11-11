import re, io, os, sys
import pickle
import logging
from jinja2 import Template
from .interpreter import Interpreter
from GeneralAgent.utils import confirm_to_run
from GeneralAgent import skills

default_import_code = """
import os, sys, math
from GeneralAgent import skills
"""

# default_libs = ' '.join(["requests", "tinydb", "openai", "jinja2", "numpy", "bs4", "playwright", "retrying", "pymupdf", "python-pptx", "python-docx", "yfinance"])
default_libs = skills.get_current_env_python_libs()

# from GeneralAgent.tools import Tools

class PythonInterpreter(Interpreter):

    python_prompt_template = """
# Run python
* Remember use print() to output
* format is : ```python\\nthe_code\\n```
* the code will be executed
* python version is {{python_version}}
* only write synchronous code
* The output display should be limited in length and should be truncated when displaying characters whose length is unknown. for example: print(a[:100])
* * Pickleable objects can be shared between different codes and variables
* Available libraries: {{python_libs}}
* The following functions can be used in code (already implemented and imported for you):
```
{{python_funcs}}
```
"""

    async_tools = []

    def __init__(self, 
                 serialize_path:str=None, 
                #  tools:Tools=None, 
                 libs: str=default_libs, 
                 import_code:str=None,
                 prompt_append=''
                 ):
        """
        Args:
            serialize_path (str): path to save the global variables, default None, which means not save, like './serialized.bin'
            libs ([str], optional): libraries can be to used. Defaults to skills.get_current_env_python_libs()
            import_code (str, optional): code to import. The tools used should be imported. Defaults to default_import_code.
            prompt_append: append to the prompt, custom prompt can be added here
        """
        from GeneralAgent import skills
        self.globals = {}  # global variables shared by all code
        self.python_libs = libs
        self.import_code = import_code or default_import_code
        self.serialize_path = serialize_path
        self.prompt_append = prompt_append
        # self.tools = tools or Tools([])
        self.globals = self.load()

    def load(self):
        if self.serialize_path is None:
            return {}
        if os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                return data['globals']
        return {}

    async def prompt(self, messages) -> str:
        from GeneralAgent import skills
        # python_funcs = self.tools.get_funs_description()
        async_funcs = '\n'.join([skills.get_function_signature(x) for x in self.async_tools])
        variables = {
            'python_libs': self.python_libs,
            'python_funcs': async_funcs,
            'python_version': skills.get_python_version()
        }
        return Template(self.python_prompt_template).render(**variables) + self.prompt_append

    @property
    def match_template(self):
        return '```python\n(.*?)\n```'

    def save(self):
        if self.serialize_path is None:
            return
        self._remove_unpickleable()
        # save
        with open(self.serialize_path, 'wb') as f:
            data = {'globals': self.globals}
            f.write(pickle.dumps(data))

    def _remove_unpickleable(self):
        if '__builtins__' in self.globals:
            self.globals.__delitem__('__builtins__')
        keys = list(self.globals.keys())
        for key in keys:
            try:
                pickle.dumps(self.globals[key])
            except Exception as e:
                self.globals.__delitem__(key)

    async def parse(self, string):
        sys_out = ''
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        if confirm_to_run():
            sys_out = await self.run_code(match.group(1))
            return sys_out.strip(), False
        else:
            return '', False

    async def run_code(self, code):
        code = self.add_print(code)
        code = self.import_code + '\n' + code
        globals_backup = self.load()
        logging.debug(code)
        sys_stdout = ''
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            exec(code, self.globals)
            success = True
        except Exception as e:
            import traceback
            sys_stdout += traceback.format_exc()
            self.globals = globals_backup
        finally:
            sys_stdout += output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        sys_stdout = sys_stdout.strip()
        if sys_stdout == '':
            sys_stdout = 'run successfully'
        return sys_stdout

    def get_variable(self, name):
        if name in self.globals:
            return self.globals[name]
        else:
            logging.warning(f"Variable {name} not found")
            return None

    def set_variable(self, name, value):
        self.globals[name] = value
        self.save()

    @classmethod
    def add_print(cls, code_string):
        pattern = r'^(\s*)(\w+)(\s*)$'
        lines = code_string.split('\n')
        for i, line in enumerate(lines):
            keywords = ['False' 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']
            if line.strip() in keywords:
                continue
            match = re.match(pattern, line)
            if match:
                lines[i] = f'{match.group(1)}print({match.group(2)}){match.group(3)}'
        return '\n'.join(lines)