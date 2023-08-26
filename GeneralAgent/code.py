import pickle
import os

class CodeWorkspace:
    def __init__(self, serialize_path=None):
        self.serialize_path = serialize_path
        self.locals = {}
        if self.serialize_path is not None and os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = f.read()
                self.locals = pickle.loads(data)

    def _save(self):
        if self.serialize_path is not None:
            with open(self.serialize_path, 'wb') as f:
                data = pickle.dumps(self.locals)
                f.write(data)

    def input(self, command):
        code = self._code_generate(command)
        success = self._code_check(code)
        if success:
            self._code_run(code)

    def _code_generate(self, command):
        # 根据命令，生成执行的代码
        code = ''
        return code

    def _code_check(self, code):
        # 验证代码是否可以执行，有没有什么问题
        return True
    
    def _code_fix(self, code, command=None):
        # 根据command，修复代码
        return code
    
    def _code_run(self, code):
        # 运行代码
        # TODO: 检测运行是否正常
        exec(code, self.locals)

    def get_variable(self, var_name):
        if var_name in self.locals:
            return self.locals[var_name]
        else:
            print("Variable not found")
            return None

    def set_variable(self, var_name, var_value):
        self.locals[var_name] = var_value