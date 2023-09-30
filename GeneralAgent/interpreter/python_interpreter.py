import re, io, os, sys
import pickle
import logging
from jinja2 import Template
from .interpreter import Interpreter

python_prompt = """
# Run python
* use print to output
* format is : ```python\\nthe_code\\n```
* the code will be executed
* python version is 3.9
* only write synchronous code
* * Pickleable objects can be shared between different codes and variables
* Available libraries: {{python_libs}}
* The following functions can be used in code (already implemented and imported for you):
```
{{python_funcs}}
```
"""

default_import_code = """
import os, sys, math
sys.path.append('../')
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web
"""

from GeneralAgent.tools import Tools

class PythonInterpreter(Interpreter):
    def __init__(self, serialize_path, tools=None, import_code=default_import_code):
        self.globals = {}  # global variables shared by all code
        self.import_code = import_code
        self.serialize_path = serialize_path
        self.tools = tools or Tools([])
        self.load()

    def load(self):
        if os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.globals = data['globals']

    def prompt(self, messages) -> str:
        python_libs = ', '.join([line.strip() for line in open(os.path.join(os.path.dirname(__file__), '../../requirements.txt'), 'r').readlines()])
        python_funcs = self.tools.get_funs_description()
        variables = {
            'python_libs': python_libs,
            'python_funcs': python_funcs
        }
        return Template(python_prompt).render(**variables)

    @property
    def match_template(self):
        return '```python\n(.*?)\n```'

    def save(self):
        # remove all unpickleable objects
        if '__builtins__' in self.globals:
            self.globals.__delitem__('__builtins__')
        keys = list(self.globals.keys())
        for key in keys:
            try:
                pickle.dumps(self.globals[key])
            except Exception as e:
                self.globals.__delitem__(key)
        # save
        with open(self.serialize_path, 'wb') as f:
            data = {'globals': self.globals}
            f.write(pickle.dumps(data))

    def parse(self, string):
        sys_out = ''
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        sys_out = self.run_code(match.group(1))
        return sys_out.strip(), False

    def run_code(self, code):
        code = self.add_print(code)
        code = self.import_code + '\n' + code
        globals_backup = pickle.dumps(self.globals)
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
            self.globals = pickle.loads(globals_backup)
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

    @classmethod
    def add_print(cls, code_string):
        pattern = r'^(\s*)(\w+)(\s*)$'
        lines = code_string.split('\n')
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                lines[i] = f'{match.group(1)}print({match.group(2)}){match.group(3)}'
        return '\n'.join(lines)