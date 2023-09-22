# Agent

import logging
logging.basicConfig(level=logging.INFO)

import os, re
from jinja2 import Template
from GeneralAgent.prompts import general_agent_prompt
from GeneralAgent.llm import llm_inference_messages
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import CodeInterpreter
from GeneralAgent.tools import Tools, google_search, wikipedia_search, scrape_web, llm

class Agent:
    def __init__(self, workspace, tools=None):
        self.workspace = workspace
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.memory = Memory(f'{workspace}/memory.json')
        self.code_workspace = CodeInterpreter(f'{workspace}/code.bin')
        self.tools = tools or Tools([google_search, wikipedia_search, scrape_web, llm])

    def run(self, content, for_node_id=None, send_message_recall=None):
        # 新增输入节点
        input_node = None
        if content is not None:
            input_node = self.insert_input(content, for_node_id)
        
        logging.info('insert node: ' + str(input_node))

        # 获取待执行节点，如果是空，就将输入节点作为待执行节点
        todo_node = self.memory.get_todo_node()
        logging.info('get_todo_node: ' + str(todo_node))
        
        if todo_node is None:
            todo_node = input_node

        # 运行
        while todo_node is not None:
            # debug输出
            logging.info('-'*50 + '<controller.memory>' + '-'*50)
            logging.info(self.memory)
            logging.info('-'*50 + '</controller.memory>' + '-'*50)
            logging.info('get_todo_node: ' + str(todo_node))
            # 如果节点含有子节点 & 全部完成，则标记为完成
            if len(todo_node.childrens) > 0 and self.memory.is_all_children_success(todo_node):
                self.memory.success_node(todo_node)
            else:
                # 执行节点
                result, new_node, is_stop = self.execute_node(todo_node)
                # 补充标题
                if todo_node.action == 'plan':
                    result = '[%s]\n' % todo_node.content + result
                # 输出消息
                send_message_recall(msg=result)
                # 是否结束
                if is_stop:
                    return new_node.node_id        
            # 获取待执行节点
            todo_node = self.memory.get_todo_node()

        return None

    def insert_input(self, content, for_node_id=None):
        logging.info('<insert_input>')
        node = MemoryNode(role='user', action='input', content=content)
        if for_node_id is None:
            self.memory.add_node(node)
        else:
            for_node = self.memory.get_node(for_node_id)
            self.memory.add_node_after(for_node, node)
            self.memory.success_node(for_node)
            self.memory.success_node(node) 
        return node
    
    def execute_node(self, node):
        # is_stop: 有疑问，需要停止
        # is_stop: 无疑问&无计划，同级别最后一个节点完成时，停止，等待用户最新输入。当没有最新输入时，计算下一个节点
        is_stop = False
        # 执行node，包括 input、task
        logging.info('execute_node for <%s>' % node.action)
        # 构建system prompt
        python_libs = ', '.join([line.strip() for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r').readlines()])
        python_funcs = self.tools.get_funs_description()
        # 送入llm的变量
        system_variables = {
            'python_libs': python_libs,
            'python_funcs': python_funcs
        }
        system_prompt = Template(general_agent_prompt).render(**system_variables)
        # 获取messages
        # messages = [{'role': 'system', 'content': system_prompt}] + self.memory.get_messages_for_node(node)
        messages = [{'role': 'system', 'content': system_prompt}] + self.memory.get_related_messages_for_node(node)
        llm_response = llm_inference_messages(messages, force_run=False, think_deep=True)
        logging.info(llm_response)
        # 完成自身节点
        self.memory.success_node(node)

        # 添加回复节点
        answer_node = MemoryNode(role='system', action='answer', content=llm_response)
        self.memory.add_node_after(node, answer_node)
        
        # step 01: 运行代码
        result = self.run_code_in_text(llm_response)
        # step 02: 替换变量
        result = self.replace_variable_in_text(result)
        # step 03: 提取计划，且计划放到回复节点中
        has_plan, result = self.extract_plan_in_text(answer_node, result)
        # step 04: 是否有疑问
        has_ask, result = self.check_has_ask(result)
        # 将result中的\n\n替换成为\n，去掉前后空白
        result = result.replace('\n\n', '\n').strip()

        # 有疑问，就停止等待结果
        if has_ask: is_stop = True

        # 无计划，完成回复节点
        if not has_plan:
            self.memory.success_node(answer_node)

        # 返回结果 & 是否停止
        return result, answer_node, is_stop
        
    def run_code_in_text(self, string):
        # 定义正则表达式匹配代码块
        pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
        # 匹配所有代码块
        matches = pattern.findall(string)
        # 逐个执行代码块并添加上结果
        for match in matches:
            # 执行代码块
            success, sys_out =  self.code_workspace.run_code('replace_python_code_blocks', match)
            # TODO: 当代码执行失败时，需要看怎么纠正
            # 干掉代码块 + 在代码后面加上答案
            string = string.replace('```python\n{}\n```'.format(match), sys_out)
            # string = string.replace('```python\n{}\n```'.format(match), '```python\n{}\n```\n'.format(match) + '```\n{}```\n'.format(sys_out))
        # 返回替换后的字符串
        return string
    
    def replace_variable_in_text(self, string):
        # 定义正则表达式匹配代码块
        pattern = re.compile(r'#\$(.*?)\$#', re.DOTALL)
        # 匹配所有代码块
        matches = pattern.findall(string)
        # 逐个执行代码块并替换原字符串
        for match in matches:
            # 执行代码块
            # exec(match)
            logging.info('replace_variable_in_text: ' + match)
            value = self.code_workspace.get_variable(match)
            # 替换原字符串中的代码块
            if value is not None:
                string = string.replace('#${}$#'.format(match), str(value))
        # 返回替换后的字符串
        return string

    def extract_plan_in_text(self, current_node, string):
        has_plan = False
        # ```plan ``` 块中，每行一个计划
        pattern = re.compile(r'```plan(.*?)```', re.DOTALL)
        # 匹配所有代码块
        matches = pattern.findall(string)
        for match in matches:
            has_plan = True
            plan_dict = structure_plan_in_level(match.strip())
            # plan_dict = structure_plan_in_plain(match.strip())
            self.add_plans_for_node(current_node, plan_dict)
            # 将 ```plan ``` 块 的```plan和```换成空格
            string = string.replace('```plan{}```'.format(match), match)
        return has_plan, string
    
    def add_plans_for_node(self, node:MemoryNode, plan_dict):
        # 最多支持4层任务
        if self.memory.get_node_level(node) >= 4:
            return
        for k, v in plan_dict.items():
            new_node = MemoryNode(role='system', action='plan', content=k.strip())
            self.memory.add_node_in(node, new_node)
            if len(v) > 0:
                self.add_plans_for_node(new_node, v)
    
    def check_has_ask(self, string):
        # 是否有疑问
        pattern = re.compile(r'###ask', re.DOTALL)
        matches = pattern.findall(string)
        has_ask = len(matches) > 0
        # 将 ###ask 换成空格
        string = string.replace('###ask', '')
        return has_ask, string
    
from collections import OrderedDict

def structure_plan_in_level(data):
    # 将plan的字符串结构化，有层级关系
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

def structure_plan_in_plain(data):
    # 将plan的字符串结构化，没有层级关系
    structured_data = OrderedDict()
    for line in data.split('\n'):
        line = line.strip()
        if not line:
            continue
        structured_data[line] = OrderedDict()
    return structured_data