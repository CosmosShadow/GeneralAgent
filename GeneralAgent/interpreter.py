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
        logging.debug('-------<code>-------')
        logging.debug(code)
        logging.debug('-------</code>-------')
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


class FileInterperter:
    def __init__(self, workspace) -> None:
        self.workspace = workspace

    def parse(self, string):
        # File Operation
        # * start: ###file write|delete|read start_index end_index file_path
        # * content: between start and end, the content of the file. If it is read, it will be automatically replaced with the content of the file. empty if delete.
        # * end: ###endfile
        # * start_index and end_index are the index of the file, starting from 0, lastest is -1
        # * file_path is the path of the file, relative to the current directory
        # * Example
        #     "write hello world to the end of the file"
        #     ###file write -1 -1 ./test.txt
        #     hello world
        #     ###endfile

        #     "read the entire file"
        #     ###file read 0 -1 ./test.txt
        #     xxxx
        #     ###endfile
            
        #     "delete line 2 to 4"
        #     ###file delete 2 4 ./test.txt
        #     ###endfile
        import re
        pattern = re.compile(r'###file (.*?)(\n.*?)?\n###endfile', re.DOTALL)
        matches = pattern.findall(string)
        for match in matches:
            operation = match[0].split(' ')
            start_index = int(operation[1])
            end_index = int(operation[2])
            file_path = operation[3]
            if operation[0] == 'write':
                content = match[1].lstrip('\n') if match[1] else ''
                self._write_file(file_path, content, start_index, end_index)
            elif operation[0] == 'delete':
                self._delete_file(file_path, start_index, end_index)
            elif operation[0] == 'read':
                content = self._read_file(file_path, start_index, end_index)
                # logging.debug(content)
                # logging.debug('###file {}\n{}\n###endfile'.format(match[0], match[1]))
                # logging.debug('###file {}\n{}\n{}\n###endfile'.format(match[0], match[1], content))
                # print('###file {}{}\n{}\n###endfile'.format(match[0], match[1], content))
                string = string.replace('###file {}{}\n###endfile'.format(match[0], match[1]), '###file {}{}\n{}\n###endfile'.format(match[0], match[1], content))
        return string
    
    def _write_file(self, file_path, content, start_index, end_index):
        file_path = os.path.join(self.workspace, file_path)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('')
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if start_index == -1:
            start_index = len(lines)
        if end_index == -1:
            end_index = len(lines)
        lines = lines[:start_index] + [content] + lines[end_index+1:]
        with open(file_path, 'w') as f:
            f.writelines(lines)

    def _delete_file(self, file_path, start_index, end_index):
        file_path = os.path.join(self.workspace, file_path)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('')
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if start_index == -1:
            start_index = len(lines)
        if end_index == -1:
            end_index = len(lines)
        lines = lines[:start_index] + lines[end_index+1:]
        with open(file_path, 'w') as f:
            f.writelines(lines)

    def _read_file(self, file_path, start_index, end_index):
        file_path = os.path.join(self.workspace, file_path)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('')
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if start_index == -1:
            start_index = len(lines)
        if end_index == -1:
            end_index = len(lines)
        content = '\n'.join(lines[start_index:end_index+1])
        return content