# Interpreter
import re, io, os, sys
import pickle
import logging
from collections import OrderedDict
from GeneralAgent.memory import MemoryNode
import abc


class Interperter(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def match_template(self) -> bool:
        pass

    @abc.abstractmethod
    def parse(self, string) -> (str, bool):
        # return output, is_stop
        pass


class BashInterperter(Interperter):
    def __init__(self, workspace='./') -> None:
        self.workspace = workspace

    @property
    def match_template(self):
        return '```shell\n(.*?)\n```'

    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        output = self._run_bash(match.group(1))
        return output.strip(), False

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
        return sys_out

class AppleScriptInterpreter(Interperter):
    @property
    def match_template(self):
        return '```applescript\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        sys_out = self._run_applescript(match.group(1))
        return sys_out.strip(), False

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
            sys_out = 'run successfully'
        return sys_out

default_import_code = """
import os, sys, math
sys.path.append('../')
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web
"""

class PythonInterpreter(Interperter):
    def __init__(self, serialize_path, import_code=default_import_code):
        self.globals = {}  # global variables shared by all code
        self.import_code = import_code
        self.serialize_path = serialize_path
        self.load()

    def load(self):
        if os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.globals = data['globals']

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


class FileInterpreter(Interperter):
    def __init__(self, workspace) -> None:
        self.workspace = workspace

    @property
    def match_template(self):
        return '###file (.*?)(\n.*?)?\n###endfile'

    def parse(self, string):
        is_stop = False
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        operation = match.group(1).split(' ')
        start_index = int(operation[1])
        end_index = int(operation[2])
        file_path = operation[3]
        if operation[0] == 'write':
            content = match.group(2).lstrip('\n') if match.group(2) else ''
            self._write_file(file_path, content, start_index, end_index)
            return 'write successfully', is_stop
        elif operation[0] == 'delete':
            self._delete_file(file_path, start_index, end_index)
            return 'delete successfully', is_stop
        elif operation[0] == 'read':
            content = self._read_file(file_path, start_index, end_index)
            return content, is_stop
    
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
        content = ''
        end_index = min(end_index + 1, len(lines))
        for index in range(start_index, end_index):
            new_add = f'[{index}]{lines[index]}\n'
            if len(content + new_add) > 2000:
                left_count = len(lines) - index
                content += f'...\n[there are {left_count} lines left]'
                break
            content += new_add
        return content.strip()
    

class PlanInterpreter(Interperter):
    def __init__(self, memory, max_plan_depth) -> None:
        self.memory = memory
        self.max_plan_depth = max_plan_depth

    @property
    def match_template(self):
        return '```runplan\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        plan_dict = self.structure_plan(match.group(1).strip())
        current_node = self.memory.current_node
        self.add_plans_for_node(current_node, plan_dict)
        return '', False
    
    def add_plans_for_node(self, node:MemoryNode, plan_dict):
        if self.memory.get_node_level(node) >= self.max_plan_depth:
            return
        for k, v in plan_dict.items():
            new_node = MemoryNode(role='system', action='plan', content=k.strip())
            self.memory.add_node_in(node, new_node)
            if len(v) > 0:
                self.add_plans_for_node(new_node, v)

    @classmethod
    def structure_plan(cls, data):
        structured_data = OrderedDict()
        current_section = [structured_data]
        for line in data.split('\n'):
            if not line.strip():
                continue
            depth = line.count('    ')
            section = line.strip()
            while depth < len(current_section) - 1:
                current_section.pop()
            current_section[-1][section] = OrderedDict()
            current_section.append(current_section[-1][section])
        return structured_data
    
class AskInterpreter(Interperter):
    @property
    def match_template(self):
        return '```ask\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        question = match.group(1).strip()
        return '', True