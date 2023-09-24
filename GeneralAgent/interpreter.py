# Interpreter
import pickle
import os
import io
import sys
import logging

import_code = """
import os, sys, math
sys.path.append('../')
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web
"""

class CodeInterpreter:
    def __init__(self, serialize_path):
        self.globals = {}  # global variables shared by all code
        self.serialize_path = serialize_path
        self.load()

    def load(self):
        if os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.globals = data['globals']

    def save(self):
        # remove __builtins__
        if '__builtins__' in self.globals:
            self.globals.__delitem__('__builtins__')
        # remove module
        # keys = list(self.globals.keys())
        # for key in keys:
        #     if str(type(self.globals[key])) == "<class 'module'>":
        #         self.globals.__delitem__(key)
        # remove non-serializable variables
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
    
    def run_code(self, code):
        code = add_print(code)
        code = import_code + '\n' + code
        globals_backup = pickle.dumps(self.globals)
        print('-------<code>-------')
        print(code)
        print('-------</code>-------')
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            exec(code, self.globals)
            success = True
        except Exception as e:
            logging.exception(e)
            self.globals = pickle.loads(globals_backup)
        finally:
            sys_stdout = output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        return success, sys_stdout

    def get_variable(self, name):
        if name in self.globals:
            return self.globals[name]
        else:
            logging.warning(f"Variable {name} not found")
            return None

    def set_variable(self, name, value):
        self.globals[name] = value

def add_print(code_string):
    import re
    pattern = r'^(\s*)(\w+)(\s*)$'
    lines = code_string.split('\n')
    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            lines[i] = f'{match.group(1)}print({match.group(2)}){match.group(3)}'
    return '\n'.join(lines)