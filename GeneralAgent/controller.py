# 控制器
# 用于控制整个系统的运行
import os
from GeneralAgent.memory import Memory, ConceptNode
from GeneralAgent.scratch import Scratch, SparkNode
from GeneralAgent.code_workspace import CodeWorkspace
from GeneralAgent.tools import Tools, google_search, wikipedia_search, scrape_web
from GeneralAgent.llm import prompt_call
from GeneralAgent.prompts import plan_prompt, plan_prompt_json_schema, write_code_prompt


class Controller:
    def __init__(self, workspace, tools=None):
        # workspace: 工作空间
        self.workspace = workspace
        # 如果目录不存在，则创建
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.memory = Memory(f'{workspace}/memory.json')
        self.scratch = Scratch(f'{workspace}/scratch.json')
        self.code_workspace = CodeWorkspace(f'{workspace}/code.bin')
        if tools is not None:
            self.tools = tools
        else:
            self.tools = Tools()
            self.tools.add_funs([google_search, wikipedia_search, scrape_web])

    def run(self, content, input_data=None, for_node_id=None, step_count=None):
        # 运行
        step = 0
        if content is not None:
            # 新增输入节点
            self.input(content, input_data, for_node_id)
            step += 1
        
        # 判断是否退出
        if step_count is not None and step == step_count: return
        
        # 运行
        while (step_count is None or (step_count is not None and step < step_count)):
            step += 1
            node = self.scratch.get_todo_node()
            if node is not None:
                if node.action in ['input', 'plan']:
                    self.plan(node); continue
                if node.action == 'output':
                    return self.output(node)
                if node.action == 'write_code':
                    self.write_code(node); continue
                if node.action == 'run_code':
                    self.run_code(node); continue
                assert False, f'未知的节点类型: {node.action}'
            else:
                print('Error: no todo node')
                print(self.scratch)
                return '抱歉，发生错误。\n请问有什么可以帮你的吗？'

    def input(self, content, input_data=None, for_node_id=None):
        print('<input>')
        input_name = None
        if input_data is not None:
            input_name = self.code_workspace.new_user_input_data(input_data)
        node = SparkNode(role='user', action='input', content=content, input_name=input_name)
        if for_node_id is None:
            self.scratch.add_node(node)
        else:
            for_node = self.scratch.get_node(for_node_id)
            # 使用after，而不是in: in会造成过多的嵌套，且不好处理退出到上一级
            self.scratch.add_node_after(node, for_node)
            # 输入内容保存到上次输出节点的输出中
            # self.code_workspace.set_variable(for_node.output, input_data)
        return node

    def output(self, node):
        print('<output>')
        # 结果占位
        self.code_workspace.set_variable(node.output_name, None)
        # 状态更新为success
        node.success_work()
        self.scratch.update_node(node)
        # 返回结果
        value = self.code_workspace.get_variable(node.input_name)
        return value

    def plan(self, node):
        print('<plan>')
        variables = {
            'task': str(node), 
            'old_plan': self.scratch.get_node_enviroment(node),
            'next_code_name': self.code_workspace.next_code_name(), 
            'next_data_name': self.code_workspace.next_data_name()
        }
        result = prompt_call(plan_prompt, variables, plan_prompt_json_schema, force_run=False, think_deep=True)
        position = result['position']
        new_plans = result['new_plans']
        # 更新计划
        self.scratch.update_plans(node, position, new_plans)

    def write_code(self, node):
        print('<write_code>')
        # 写代码
        node_enviroment = self.scratch.get_node_enviroment(node)
        # 从 ./requirements.txt 中读取依赖库
        python_libs = '\n'.join([line.strip() for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r').readlines()])
        # 从 ./tools.py 中读取函数
        python_funcs = self.tools.get_funs_description()
        variables = {
            'python_libs': python_libs,
            'python_funcs': python_funcs,
            'task': node.content,
            'task_enviroment': node_enviroment,
            }
        code = prompt_call(write_code_prompt, variables, think_deep=True)
        # TODO: 复合check一遍
        # 保存代码
        self.code_workspace.set_variable(node.output_name, code)
        # TODO: 可能写不成功
        success = True
        reason = 'xxxxx'
    
        if success:
            self.scratch.success_node(node)
        else:
            self.scratch.fail_node(node)
            input_name = self.code_workspace.new_variable(reason)
            new_node = SparkNode('system', 'plan', content='写代码报错', input_name=input_name)
            self.scratch.add_node_after(new_node, node)
            print('Error: write code fail')

    def run_code(self, node):
        print('<run_code>')
        # 提取代码
        code = self.code_workspace.get_variable(node.input_name)
        # 运行代码
        success, sys_stdio = self.code_workspace.run_code(node.content, code)
        # TODO: 如果失败，最多修复2次

        # 更新状态
        if success:
            self.scratch.success_node(node)
        else:
            self.scratch.fail_node(node)
            input_name = self.code_workspace.new_variable(sys_stdio)
            new_node = SparkNode('system', 'plan', content='代码运行报错', input_name=input_name)
            self.scratch.add_node_after(new_node, node)
            print('Error: run code fail')