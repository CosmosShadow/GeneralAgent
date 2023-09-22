# CodeInterpreter
import pickle
import os
import io
import sys
import logging

import_string = """
import math
import os
import sys
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools, llm
"""

class CodeInterpreter:
    def __init__(self, serialize_path):
        self.locals = {}
        self.serialize_path = serialize_path
        self.load()

    def load(self):
        if os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.locals = data['locals']

    def save(self):
        # Remove non-serializable variables __builtins__ and module
        if '__builtins__' in self.locals:
            self.locals.__delitem__('__builtins__')
        keys = list(self.locals.keys())
        for key in keys:
            if str(type(self.locals[key])) == "<class 'module'>":
                self.locals.__delitem__(key)
        with open(self.serialize_path, 'wb') as f:
            data = {'locals': self.locals}
            f.write(pickle.dumps(data))
    
    def run_code(self, code):
        code = add_print(code)
        code = import_string + '\n' + code
        old_locals_bin = pickle.dumps(self.locals)
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            exec(code, self.locals)
            success = True
        except Exception as e:
            logging.exception(e)
            self.locals = pickle.loads(old_locals_bin)
        finally:
            sys_stdout = output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        return success, sys_stdout

    def get_variable(self, name):
        if name in self.locals:
            return self.locals[name]
        else:
            logging.warning(f"Variable {name} not found")
            return None

    def set_variable(self, name, value):
        self.locals[name] = value


def add_print(code_str):
    """add print for varible line, for example: a = 1\na => a = 1\nprint(a)"""
    import re
    var_pattern = r'\b[a-zA-Z_]\w*\b\s*'
    lines = code_str.split('\n')
    for i, line in enumerate(lines):
        match = re.search(var_pattern, line)
        if match:
            var_name = match.group().strip()
            lines[i] = f'{var_name} = print({var_name})'
    new_code_str = '\n'.join(lines)
    return new_code_str