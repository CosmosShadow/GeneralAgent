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

class BashInterperter:
    def __init__(self, workspace='./') -> None:
        self.workspace = workspace

    def parse(self, string):
        # ```shell\nxxx\n```
        # logging.info(string)
        import re
        pattern = re.compile(r'```shell\n(.*?)\n```', re.DOTALL)
        matches = pattern.findall(string)
        sys_out = None
        for match in matches:
            sys_out = self._run_bash(match)
        return string, sys_out

    def _run_bash(self, content):
        sys_out = ''
        import subprocess
        if 'python ' in content:
            content = content.replace('python ', 'python3 ')
        try:
            p = subprocess.Popen(content, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            pass
        finally:
            sys_out, err = p.communicate()
            sys_out = sys_out.decode('utf-8')
        print('\n' + sys_out + '\n')
        return sys_out
        # alternative: os.system('ls')

class AppleScriptInterperter:
    def parse(self, string):
        # ```applescript\nxxx\n```
        # logging.info(string)
        import re
        pattern = re.compile(r'```applescript\n(.*?)\n```', re.DOTALL)
        matches = pattern.findall(string)
        sys_out = None
        for match in matches:
            sys_out = self._run_applescript(match)
            # 替换掉```applescript\nxxx\n```，替换成执行结果
            string = string.replace('```applescript\n{}\n```'.format(match), sys_out)
        return string, sys_out

    def _run_applescript(self, content):
        content = content.replace('"', '\\"')
        sys_out = ''
        import subprocess
        try:
            p = subprocess.Popen('osascript -e "{}"'.format(content), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            pass
        finally:
            sys_out, err = p.communicate()
            sys_out = sys_out.decode('utf-8')
        sys_out = sys_out.strip()
        if sys_out == '':
            print('run successfully')
        return sys_out
        # alternative: os.system('ls')


class PythonInterpreter:
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

    def parse(self, string):
        import re
        sys_out = ''
        pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
        matches = pattern.findall(string)
        for code in matches:
            success, sys_out = self.run_code(code)
            string = string.replace('```python\n{}\n```'.format(code), sys_out)
            print(sys_out)
        return string, sys_out
    
    def run_code(self, code):
        code = self.add_print(code)
        code = import_code + '\n' + code
        globals_backup = pickle.dumps(self.globals)
        logging.debug('-------<code>-------')
        logging.debug(code)
        logging.debug('-------</code>-------')
        sys_stdout = ''
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            exec(code, self.globals)
            success = True
        except Exception as e:
            # logging.exception(e)
            # 获取全部输出的日志
            import traceback
            sys_stdout += traceback.format_exc()
            self.globals = pickle.loads(globals_backup)
        finally:
            sys_stdout += output.getvalue()
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

    @classmethod
    def add_print(cls, code_string):
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
        # if .py file, remove ```python  and ``` pair
        if file_path.endswith('.py'):
            content = content.replace('```python', '')
            content = content.replace('```', '')
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