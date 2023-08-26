# CodeWorkspace: 
# 代码工作空间，就是Agent的工作空间
# 想法和Action的串联物，相当于人的肌肉，受控于神经元，操作工具，完成任务

import pickle
import os


class CodeWorkspace:
    def __init__(self, serialize_path=None):
        # serialize_path: 保存工作环境的地址
        self.locals = {}    # 本地变量，代码运行时的环境
        self.logs = []       # 运行时的日志，应该是一个三元组 (命令，代码，结果)
        self.serialize_path = serialize_path    # 序列化地址
        self._load()

    def _load(self):
        # 加载
        if self.serialize_path is not None and os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.locals = data['locals']
                self.logs = data['logs']

    def _save(self):
        # 保存，即序列化
        if self.serialize_path is not None:
            with open(self.serialize_path, 'wb') as f:
                data = {'locals': self.locals, 'logs': self.logs}
                f.write(pickle.dumps(data))

    def input(self, command):
        # 输入命令(string)，生成代码并执行
        retry_count = 3
        # 生成代码
        code = self._code_generate(command)
        # 检查&修复代码
        for _ in range(retry_count):
            check_success = self._code_check(code)
            if check_success: break
            code = self._code_fix(code, command=command)
        # 执行代码&修复代码
        for _ in range(retry_count):
            run_success = self._code_run(code)
            if run_success: break
            code = self._code_fix(code, command=command, error=True)
        # 保存现场
        if run_success:
            self._save()
        return run_success

    def _code_generate(self, command):
        # 根据命令，生成执行的代码
        # TODO
        code = ''
        return code

    def _code_check(self, code):
        # TODO: 
        # 验证代码是否可以执行，有没有什么问题
        return True
    
    def _code_fix(self, code, command=None, error=None):
        # TODO: 
        # 根据command，修复代码
        return code
    
    def _code_run(self, code):
        # 运行代码
        # TODO: 获取运行日志
        old_locals_bin = pickle.dumps(self.locals)
        try:
            exec(code, self.locals)
            return True
        except Exception as e:
            # 异常情况，恢复环境
            self.locals = pickle.loads(old_locals_bin)
            print(e)
            return False

    def get_variable(self, var_name):
        if var_name in self.locals:
            return self.locals[var_name]
        else:
            print("Variable not found")
            return None

    def set_variable(self, var_name, var_value):
        self.locals[var_name] = var_value