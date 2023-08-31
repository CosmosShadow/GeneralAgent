# 控制器
# 用于控制整个系统的运行
from memory import Memory, ConceptNode
from scratch import Scratch, SparkNode
from code import CodeWorkspace
from tools import Tools
from llm import prompt_call
from prompts import write_code_prompt


class Controller:
    def __init__(self, workspace):
        # workspace: 工作空间
        self.workspace = workspace
        self.memory = Memory(f'{workspace}/memory.json')
        self.scratch = Scratch(f'{workspace}/scratch.json')
        self.code_workspace = CodeWorkspace(f'{workspace}/code.bin')
        self.tools = Tools()

    def run(self, input_data):
        pass

    # 'root', 'input', 'output', 'plan', 'think', 'write_code', 'run_code'
    def input(self, node):
        pass

    def output(self, node):
        pass

    def plan(self, node):
        pass

    def think(self, node):
        pass

    def write_code(self, node):
        # 写代码
        node_env = self.scratch.get_node_enviroment(node)
        variables = {'task': node.task, 'node_env': node_env}
        code = prompt_call(write_code_prompt, variables, think_deep=True)
        # 保存代码
        self.code_workspace.set_variable(node.output, code)

    def run_code(self, node):
        # 提取代码
        code = self.code_workspace.get_variable(node.input)
        # 运行代码
        run_success, sys_stdio = self.code_workspace.run_code(code.task, code)
        return run_success, sys_stdio

    def code_generate(self, command):
        # 根据命令，生成执行的代码
        # TODO
        code = ''
        return code

    def _code_check(self, command, code):
        # TODO: 
        # 验证代码是否可以执行，有没有什么问题
        return True
    
    def _code_fix(self, code, command=None, error=None):
        # TODO: 
        # 根据command，修复代码
        return code