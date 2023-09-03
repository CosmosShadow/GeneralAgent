# CodeWorkspace: 
# 代码工作空间，就是Agent的工作空间
# concept和action的串联物，相当于人的肌肉，受控于神经元，操作工具，完成任务

import pickle
import os
import io
import sys
import logging

class CodeBlock:
    def __init__(self, type, command, code, log, name=None, value=None):
        assert type in ['set', 'get', 'command']
        self.type = type        # 类型, ['set', 'get', 'command']
        self.command = command  # 命令
        self.code = code
        self.log = log            # 运行日志
        self.name = name    # 在set和get使用
        self.value = value     # 在set使用

    def __str__(self):
        if self.type == 'set':
            return f"# set: \n{self.name}={self.value}"
        if self.type == 'get':
            return f"# get: {self.name}"
        if self.type == 'command':
            return f"# command: {self.command} \n {self.code}"
        return f"{self.type} {self.command} {self.name} {self.value} {self.code} {self.log}"

default_init_code = """
import os
import sys
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools, llm
"""

class CodeWorkspace:
    def __init__(self, serialize_path=None, init_code=default_init_code):
        # serialize_path: 保存工作环境的地址
        self.locals = {}    # 本地变量，代码运行时的环境
        self.code_block_list = []       # 代码块列表
        self.serialize_path = serialize_path    # 序列化地址
        if serialize_path is None:
            print("Warning: serialize_path is None, CodeWorkspace will not be serialized")
        load_success = self._load()
        if load_success is False:
            # 初始化
            self.run_code('init', init_code)

    def _load(self):
        # 加载
        if self.serialize_path is not None and os.path.exists(self.serialize_path):
            # print('加载序列化文件')
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.locals = data['locals']
                self.code_block_list = data['code_block_list']
                return True
        else:
            # print('未加载序列化文件')
            return False

    def _save(self):
        # 保存，即序列化
        if self.serialize_path is not None:
            with open(self.serialize_path, 'wb') as f:
                # 删除不可序列化的变量: __builtins__和module
                if '__builtins__' in self.locals:
                    self.locals.__delitem__('__builtins__')
                keys = list(self.locals.keys())
                for key in keys:
                    if str(type(self.locals[key])) == "<class 'module'>":
                        self.locals.__delitem__(key)
                # 保存
                data = {'locals': self.locals, 'code_block_list': self.code_block_list}
                f.write(pickle.dumps(data))
    
    def run_code(self, command, code):
        # 运行代码: 每次运行代码时，需要重新加载环境，或者外部需要使用到的库，因为locals不能序列化module
        old_locals_bin = pickle.dumps(self.locals)
        # 重定向输出
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            # 运行代码
            exec(code, self.locals)
            success = True
        except Exception as e:
            # 异常情况，恢复环境
            print('代码运行异常')
            logging.exception(e)
            self.locals = pickle.loads(old_locals_bin)
        finally:
            # 获取结果，并恢复输出
            sys_stdout = output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            # 保存代码块
            code_block = CodeBlock(type='command', command=command, code=code, log=sys_stdout)
            self.code_block_list.append(code_block)
            # 保存现场
            self._save()
        # print(f'<run_code>\ncommand={command} \nsucess={success} \nsys_stdout:\n{sys_stdout}</run_code>')
        return success, sys_stdout

    def get_variable(self, var_name):
        if var_name in self.locals:
            # 保存代码块
            code_block = CodeBlock(type='get', command=None, code=None, log=None, name=var_name)
            self.code_block_list.append(code_block)
            # 保存现场
            self._save()
            return self.locals[var_name]
        else:
            print("Variable not found")
            return None

    def set_variable(self, var_name, var_value):
        print('set_variable', var_name, var_value)
        # raise ValueError('set_variable')
        self.locals[var_name] = var_value
        # 保存代码块
        code_block = CodeBlock(type='set', command=None, code=None, log=None, name=var_name, value=var_value)
        self.code_block_list.append(code_block)
        # 保存现场
        self._save()

    def new_variable(self, input_data):
        name = self.next_data_name()
        self.set_variable(name, input_data)
        return name
    
    def next_code_name(self):
        print(self.locals)
        prefix = 'code_'
        code_names = [x for x in self.locals.keys() if x.startswith('prefix')]
        index = len(code_names)
        name = f'{prefix}{index}'
        return name
    
    def next_data_name(self):
        prefix = 'data_'
        input_data_names = [x for x in self.locals.keys() if x.startswith('prefix')]
        index = len(input_data_names)
        name = f'{prefix}{index}'
        return name

    def get_code_sheet(self):
        # 获取代码清单
        return '\n\n'.join([str(code_block) for code_block in self.code_block_list])