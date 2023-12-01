import re, io, os, sys
import pickle
import logging
from jinja2 import Template
from .interpreter import Interpreter
from GeneralAgent.utils import confirm_to_run
from GeneralAgent import skills
import asyncio

default_import_code = """
import os, sys, math
from GeneralAgent import skills
"""

# default_libs = ' '.join(["requests", "tinydb", "openai", "jinja2", "numpy", "bs4", "playwright", "retrying", "pymupdf", "python-pptx", "python-docx", "yfinance"])
# default_libs = skills.get_current_env_python_libs()
default_libs = ''

# from GeneralAgent.tools import Tools

class SyncPythonInterpreter(Interpreter):
    """
    Sync Python Interpreter: run python code in the interpreter. Not same namespace with the agent & Can Only run synchronous code
    """

    output_match_start_pattern = '```python\n'
    output_match_pattern = '```python\n(.*?)\n```'

    python_prompt_template = """
# Run python
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

    function_tools = []

    def __init__(self, 
                 serialize_path:str=None, 
                 libs: str=default_libs, 
                 import_code:str=None,
                 prompt_append='',
                 stop_wrong_count = 2
                 ):
        """
        Args:
            serialize_path (str): path to save the global variables, default None, which means not save, like './serialized.bin'
            libs ([str], optional): libraries can be to used. Defaults to skills.get_current_env_python_libs()
            import_code (str, optional): code to import. The tools used should be imported. Defaults to default_import_code.
            prompt_append: append to the prompt, custom prompt can be added here
            stop_wrong_count: stop running when the code is wrong for stop_wrong_count times
        """
        from GeneralAgent import skills
        self.globals = {}  # global variables shared by all code
        self.python_libs = libs
        self.import_code = import_code or default_import_code
        self.serialize_path = serialize_path
        self.prompt_append = prompt_append
        # self.tools = tools or Tools([])
        self.globals = self.load()
        # count the number of times the code is wrong, and stop running when it reaches the threshold
        self.run_wrong_count = 0
        self.stop_wrong_count = stop_wrong_count

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
        funtions = '\n\n'.join([skills.get_function_signature(x) for x in self.function_tools])
        variables = {
            'python_libs': self.python_libs,
            'python_funcs': funtions,
            'python_version': skills.get_python_version()
        }
        return Template(self.python_prompt_template).render(**variables) + self.prompt_append

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

    async def output_parse(self, string) -> (str, bool):
        sys_out = ''
        pattern = re.compile(self.output_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        if confirm_to_run():
            sys_out, stop = await self.run_code(match.group(1))
            result = 'python runs result:\n' + sys_out.strip()
            return result, stop
        else:
            return '', False

    async def run_code(self, code):
        stop = False
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
            self.run_wrong_count = 0
        except Exception as e:
            import traceback
            sys_stdout += traceback.format_exc()
            self.globals = globals_backup
            self.run_wrong_count += 1
            if self.run_wrong_count >= self.stop_wrong_count:
                stop = True
        finally:
            sys_stdout += output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        sys_stdout = sys_stdout.strip()
        if sys_stdout == '':
            sys_stdout = 'run successfully'
        return sys_stdout, stop

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
    def add_print_old(cls, code_string):
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
    
    @classmethod
    def add_print(cls, code_string):
        from GeneralAgent import skills
        code = code_string.strip()
        lines = code.split('\n')
        if len(lines) > 0:
            last_line = lines[-1]
            if skills.python_line_is_variable_expression(last_line):
                last_line = f'print({last_line})'
                lines[-1] = last_line
        return '\n'.join(lines)

def _remove_unpickleable(namespace):
    import pickle
    if '__builtins__' in namespace:
        namespace.__delitem__('__builtins__')
    keys = list(namespace.keys())
    for key in keys:
        try:
            pickle.dumps(namespace[key])
        except Exception as e:
            namespace.__delitem__(key)
    return namespace


def code_wrap(code, namespace):
    lines = code.split('\n')
    code = '\n    '.join(lines)
    variables = '\n    '.join([f'{name} = globals()[\'{name}\']' for name, value in namespace.items()])
    content = f"""
import asyncio

def _remove_unpickleable(namespace):
    import pickle
    if '__builtins__' in namespace:
        namespace.__delitem__('__builtins__')
    keys = list(namespace.keys())
    for key in keys:
        try:
            pickle.dumps(namespace[key])
        except Exception as e:
            namespace.__delitem__(key)
    for name in ['__name', '__value', '__namespace']:
        if name in namespace:
            namespace.__delitem__(name)
    return namespace

__namespace = None

async def __main():
    {variables}
    {code}
    global __namespace
    __namespace = _remove_unpickleable(locals().copy())
"""
    # print('----------<code>--------')
    # print(content)
    # print('----------</code>--------')
    return content


class AsyncPythonInterpreter(SyncPythonInterpreter):
    """
    Sync Python Interpreter: run python code in the interpreter. Same namespace with the agent & Can run async code
    """

    python_prompt_template = """
# Run python
- format is : ```python\\nthe_code\\n```
- the code will be executed
- python version is {{python_version}}
- Pickleable objects can be shared between different codes and variables
- The output display should be limited in length and should be truncated when displaying characters whose length is unknown. for example: print(a[:100])
- Available libraries: {{python_libs}}
Complete the entire process in one code instead of writing multiple codes to run step by step. For example, the following code is allowed:
```python
# step 1
a = fun1(xx)
# step 2
c = fun2(a)
# step 3
d = fun3(c)
...
```
- The following functions can be used in code (already implemented and imported for you):
```
{{python_funcs}}
```
"""

    async def run_code(self, code):
        stop = False
        code = self.add_print(code)
        code = code_wrap(code, self.globals)
        code = self.import_code + '\n' + code
        # print('hello')
        # print(code)
        # print(self.function_tools)
        globals_backup = self.load()
        logging.debug(code)
        sys_stdout = ''
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            # exec(code, self.globals)
            # run async python code
            local_vars = self.globals
            # register functions
            for fun in self.function_tools:
                local_vars[fun.__name__] = fun
            # print(local_vars)
            exec(code, local_vars, local_vars)
            main_function = local_vars['__main']
            await asyncio.create_task(main_function())
            local_vars = _remove_unpickleable(local_vars)
            local_vars = local_vars['__namespace']
            # remove functions
            for fun in self.function_tools:
                if fun.__name__ in local_vars:
                    local_vars.__delitem__(fun.__name__)
            self.globals = local_vars

            success = True
            self.run_wrong_count = 0
        except Exception as e:
            import traceback
            sys_stdout += traceback.format_exc()
            self.globals = globals_backup
            logging.exception((e))
            self.run_wrong_count += 1
            if self.run_wrong_count >= self.stop_wrong_count:
                stop = True
        finally:
            sys_stdout += output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        sys_stdout = sys_stdout.strip()
        if sys_stdout == '':
            sys_stdout = 'run successfully'
        return sys_stdout, stop
    

# class PythonInterpreter(AsyncPythonInterpreter):
#     """
#     Sync Python Interpreter: run python code in the interpreter. Same namespace with the agent & Can run async code
#     """
#     pass