# Agent

import os, re
import asyncio
import logging
import datetime
import platform
from jinja2 import Template

from GeneralAgent.prompts import general_agent_prompt
from GeneralAgent.llm import llm_inference
from GeneralAgent.tools import Tools
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import Interpreter, PythonInterpreter, FileInterpreter, BashInterperter, AppleScriptInterpreter, PlanInterpreter


class Agent:
    def __init__(self, workspace, tools=None, max_plan_depth=4):
        self.workspace = workspace
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.memory = Memory(serialize_path=f'{workspace}/memory.json')
        self.tools = tools or Tools([])
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.os_version = get_os_version()

        self.python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        self.bash_interpreter = BashInterperter('./')
        self.applescript_interpreter = AppleScriptInterpreter()
        self.file_interpreter = FileInterpreter('./')
        self.plan_interperter = PlanInterpreter(self.memory, max_plan_depth)
        self.interpreters = [self.python_interpreter, self.bash_interpreter, self.applescript_interpreter, self.file_interpreter, self.plan_interperter]


    async def run(self, input=None, for_node_id=None, output_recall=None):
        self.is_running = True
        input_node = self._insert_node(input, for_node_id) if input is not None else None
        todo_node = self.memory.get_todo_node() or input_node
        while todo_node is not None:
            if len(todo_node.childrens) > 0 and self.memory.is_all_children_success(todo_node):
                self.memory.success_node(todo_node)
            else:
                result, new_node, is_stop = self._execute_node(todo_node)
                if todo_node.action == 'plan':
                    result = f'[{todo_node.content}]\n{result}'
                if output_recall is not None:
                    await output_recall(result)
                if is_stop:
                    return new_node.node_id        
            todo_node = self.memory.get_todo_node()
            await asyncio.sleep(0)
            if self.stop_event.is_set():
                self.is_running = False
                return None
        self.is_running = False
        return None
    
    def stop(self):
        self.stop_event.set()

    def _insert_node(self, input, for_node_id=None):
        node = MemoryNode(role='user', action='input', content=input)
        if for_node_id is None:
            self.memory.add_node(node)
        else:
            for_node = self.memory.get_node(for_node_id)
            self.memory.add_node_after(for_node, node)
            self.memory.success_node(for_node)
            self.memory.success_node(node) 
        return node
    
    def _execute_node(self, node):
        python_libs = ', '.join([line.strip() for line in open(os.path.join(os.path.dirname(__file__), '../requirements.txt'), 'r').readlines()])
        python_funcs = self.tools.get_funs_description()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_variables = {
            'now': now,
            'os_version': self.os_version,
            'python_libs': python_libs,
            'python_funcs': python_funcs
        }
        system_prompt = Template(general_agent_prompt).render(**system_variables)
        messages = [{'role': 'system', 'content': system_prompt}] + self.memory.get_related_messages_for_node(node)

        # add answer node and set current node
        answer_node = MemoryNode(role='system', action='answer', content='')
        self.memory.add_node_after(node, answer_node)
        self.memory.set_current_node(answer_node)

        # TODO: when messages exceed limit, cut it

        result = ''
        response = llm_inference(messages)
        for token in response:
            if token is None: break
            result += token
            for interpreter in self.interpreters:
                match = re.compile(interpreter.match_template, re.DOTALL).search(result)
                if match is not None:
                    output = interpreter.parse(result)
                    result = result.strip() + '\n' + output.strip()
                    break
        
        # process: file -> applescript -> bash -> code -> plan -> ask
        
        result = self.file_interpreter.parse(result)
        result, apple_sys_out = self.applescript_interpreter.parse(result)
        result, bash_sys_out = self.bash_interpreter.parse(result)
        result, python_sys_out = self.python_interpreter.parse(result)
        resutl = self.plan_interperter.parse(result)
        has_ask, result = check_has_ask(result)
        result = result.replace('\n\n', '\n').strip()

        self.memory.success_node(node)
        if not has_plan:
            self.memory.success_node(answer_node)

        if apple_sys_out is not None and apple_sys_out.strip() != '':
            new_node = MemoryNode(role='user', action='input', content=apple_sys_out)
            self.memory.add_node_after(answer_node, new_node)
        if bash_sys_out is not None and bash_sys_out.strip() != '':
            new_node = MemoryNode(role='user', action='input', content=bash_sys_out)
            self.memory.add_node_after(answer_node, new_node)
        if python_sys_out is not None and python_sys_out.strip() != '' and 'Traceback' in python_sys_out:
            new_node = MemoryNode(role='user', action='input', content=python_sys_out)
            self.memory.add_node_after(answer_node, new_node)

        is_stop = has_ask
        
        return result, answer_node, is_stop


def check_has_ask(string):
    pattern = re.compile(r'```ask', re.DOTALL)
    has_ask = pattern.search(string) is not None
    string = pattern.sub('', string)
    return has_ask, string



def get_os_version():
    system = platform.system()
    if system == 'Windows':
        version = platform.version()
        return f"Windows version: {version}"
    elif system == 'Darwin':
        version = platform.mac_ver()[0]
        return f"macOS version: {version}"
    elif system == 'Linux':
        dist = platform.linux_distribution()
        if dist[0] == 'CentOS':
            version = dist[1]
            return f"CentOS version: {version}"
        elif dist[0] == 'Ubuntu':
            version = dist[1]
            return f"Ubuntu version: {version}"
    else:
        return "Unknown system"