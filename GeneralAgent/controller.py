# 控制器
# 用于控制整个系统的运行
from memory import Memory, ConceptNode
from scratch import Scratch, SparkNode
from code_workspace import CodeWorkspace
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

    # 'root', 'input', 'output', 'plan', 'think', 'write_code', 'run_code'

    def run(self, task, input_data=None, for_node_id=None):
        # 新增输入节点
        self.input(task, input_data, for_node_id)

        # 不应该那么早执行plan: plan只是占位，由于output后用户输入，后面可能会调整plan
        # # 计划
        # while True:
        #     plan_node = self.scratch.get_next_plan_node()
        #     if plan_node is None:
        #         break
        #     else:
        #         self.plan(plan_node)
        
        # 运行
        while True:
            node = self.scratch.get_todo_node()
            if node is not None:
                if node.type in ['input', 'plan']:
                    self.plan(node)
                    continue
                if node.type == 'output':
                    return self.output(node)
                if node.type == 'answer':
                    self.answer(node)
                    continue
                if node.type == 'write_code':
                    self.write_code(node)
                    continue
                if node.type == 'run_code':
                    success, sys_stdio = self.run_code(node)
                    if not success:
                        new_node = SparkNode('system', 'plan', task='代码运行报错', input=sys_stdio, output=None)
                        self.scratch.add_node_after(new_node, node)
                        print('Error: run code fail')
                    continue
                assert False, f'未知的节点类型: {node.type}'
            else:
                print('Error: no todo node')
                return '抱歉，发生错误。\n请问有什么可以帮你的吗？'

    def input(self, task, input_data=None, for_node_id=None):
        input = None
        if input_data is not None:
            input = self.code_workspace.new_user_input_data(input_data)
        node = SparkNode('user', 'input', task=task, input=input)
        if for_node_id is None:
            self.scratch.add_node(node)
        else:
            for_node = self.scratch.get_node(for_node_id)
            # 使用after，而不是in: in会造成过多的嵌套，且不好处理退出到上一级
            self.scratch.add_node_after(node, for_node)
            # 输入内容保存到上次输出节点的输出中
            self.code_workspace.set_variable(for_node.output, input_data)
        return node

    def output(self, node):
        # 结果占位
        self.code_workspace.set_variable(node.output, None)
        # 状态更新为success
        node.success_work()
        self.scratch.update_node(node)
        # 返回结果
        return self.code_workspace.get_variable(node.input)

    def plan(self, node):
        pass

    def answer(self, node):
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
        success, sys_stdio = self.code_workspace.run_code(code.task, code)
        # TODO: 如果失败，最多修复2次
        # 添加新的节点不？
        return success, sys_stdio

    # def code_generate(self, command):
    #     # 根据命令，生成执行的代码
    #     # TODO
    #     code = ''
    #     return code

    # def _code_check(self, command, code):
    #     # TODO: 
    #     # 验证代码是否可以执行，有没有什么问题
    #     return True
    
    # def _code_fix(self, code, command=None, error=None):
    #     # TODO: 
    #     # 根据command，修复代码
    #     return code