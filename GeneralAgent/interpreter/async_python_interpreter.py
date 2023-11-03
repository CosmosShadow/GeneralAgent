import io, sys
import logging
from .python_interpreter import PythonInterpreter
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


class AsyncPythonInterpreter(PythonInterpreter):

    python_prompt_template = """
# Run python
* Remember use print() to output
* format is : ```python\\nthe_code\\n```
* the code will be executed
* python version is 3.9
* * Pickleable objects can be shared between different codes and variables
* Available libraries: {{python_libs}}
* The following functions can be used in code (already implemented and imported for you):
```
{{python_funcs}}
```
"""

    async def run_code(self, code):
        code = self.add_print(code)
        code = code_wrap(code, self.globals)
        code = self.import_code + '\n' + code
        # print('hello')
        # print(code)
        # print(self.async_tools)
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
            for fun in self.async_tools:
                local_vars[fun.__name__] = fun
            # print(local_vars)
            exec(code, local_vars, local_vars)
            main_function = local_vars['__main']
            await asyncio.create_task(main_function())
            local_vars = _remove_unpickleable(local_vars)
            local_vars = local_vars['__namespace']
            # remove functions
            for fun in self.async_tools:
                if fun.__name__ in local_vars:
                    local_vars.__delitem__(fun.__name__)
            self.globals = local_vars

            success = True
        except Exception as e:
            import traceback
            sys_stdout += traceback.format_exc()
            self.globals = globals_backup
            logging.exception((e))
        finally:
            sys_stdout += output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        sys_stdout = sys_stdout.strip()
        if sys_stdout == '':
            sys_stdout = 'run successfully'
        return sys_stdout