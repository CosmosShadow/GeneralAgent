# Agent
import os
import logging
from GeneralAgent.memory import NormalMemory, StackMemory
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.interpreter import KnowledgeInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter
from .abs_agent import AbsAgent


class NormalAgent(AbsAgent):
    def __init__(self, role:str=None, functions:list=[], workspace:str=None, model_type='smart', self_call=False, continue_run=False):
        """
        @role: str, Agent角色描述，例如"你是一个小说家"，默认为None
        @functions: list, Agent可用的函数(工具)列表，默认为[]
        @workspace: str, Agent序列化目录地址，如果目录不存在会自动创建，如果workspace不为None，则会从workspace中加载序列化的memory和python代码。默认None表示不序列化，不加载。
        @model_type: str, 模型类型，'smart', 'normal', or 'long', 默认为'smart'.
        @self_call: bool, 是否开启自我调用(Agent可以写代码来自我调用完成复杂任务), 默认为False.
        @continue_run: bool, 是否自动继续执行。Agent在任务没有完成时，是否自动执行。默认为True.
        """
        super().__init__(workspace)
        self.memory = StackMemory(serialize_path=self._memory_path)
        self.role_interpreter = RoleInterpreter(role=role, self_call=self_call)
        self.python_interpreter = PythonInterpreter(self, serialize_path=self._python_path)
        self.python_interpreter.function_tools = functions
        self.model_type = model_type
        self.continue_run = continue_run
        self.interpreters = [self.role_interpreter, self.python_interpreter]

    @property
    def _memory_path(self):
        if self.workspace is None:
            return None
        else:
            return os.path.join(self.workspace, 'memory.json')
    
    @property
    def _python_path(self):
        if self.workspace is None:
            return None
        else:
            return os.path.join(self.workspace, 'code.bin')

    @classmethod
    def empty(cls, workspace='./'):
        """
        empty agent, only role interpreter and memory, work like a basic LLM chatbot
        """
        agent = cls(workspace)
        agent.interpreters = [RoleInterpreter()]
        return agent

    @classmethod
    def default(cls, workspace='./'):
        """
        default agent, with all interpreters
        @workspace: str, workspace path
        """
        agent = cls(workspace)
        role_interpreter = RoleInterpreter()
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        agent.interpreters = [role_interpreter, agent.python_interpreter, bash_interpreter, applescript_interpreter]
        return agent
    
    @property
    def functions(self):
        return self.python_interpreter.function_tools

    @functions.setter
    def functions(self, new_value):
        self.python_interpreter.function_tools = new_value

    @property
    def role(self):
        return self.role_interpreter.role
    
    @role.setter
    def role(self, new_value):
        self.role_interpreter.role = new_value

    @classmethod
    def with_functions(
        cls,
        functions=[],
        system_prompt=None,
        role_prompt=None,
        self_control=False,
        search_functions=False,
        workspace = './',
        model_type='smart',
        variables=None,
        knowledge_query_function=None,
        continue_run=True,
        ):
        """
        agent with functions
        @functions: list, [function1, function2, ...]
        @system_prompt: str, system prompt，完全替换默认的system_prompt，且这时候 self_control & search_functions无效
        @role_prompt: str, role prompt，在system_prompt的后面添加的prompt
        @self_control: bool, 是否开启自控
        @search_functions: bool, 是否开启搜索函数
        @workspace: str, workspace path
        @model_type: str, 'smart', 'normal', or 'long'
        @variables: dict, embed variables to python interpreter, like {'a': a, 'variable_name': variable_value}, then Agent can use the variables in python interpreter like `variable_name`
        @knowledge_query_function: function, knowledge query function
        @continue_run: bool, 是否自动继续执行。Agent在任务没有完成时，是否自动执行。默认为False
        @new: bool, 是否新建一个Agent，如果为True，则会删除之前的memory
        """
        agent = cls(workspace)
        role_interpreter = RoleInterpreter(system_prompt=system_prompt, self_control=self_control, search_functions=search_functions)
        agent.python_interpreter.function_tools = functions
        interpreter_list = [role_interpreter, agent.python_interpreter]
        if knowledge_query_function is not None:
            knowledge_interpreter = KnowledgeInterperter(knowledge_query_function)
            interpreter_list.append(knowledge_interpreter)
        agent.interpreters = interpreter_list
        agent.model_type = model_type
        if role_prompt is not None:
            agent.add_role_prompt(role_prompt)
        if variables is not None:
            for key, value in variables.items():
                agent.python_interpreter.set_variable(key, value)
        agent.continue_run = continue_run
        return agent

    def run(self, input, return_type=str, stream_callback=None, user_check=False):
        """
        代码调用执行input命令
        """
        # 代码调用agent执行，直接run_level+1
        self.run_level += 1
        from GeneralAgent import skills
        if stream_callback is not None:
            self.output_callback = stream_callback
        result = self._run(input, return_type)
        if user_check:
            response = skills.input('请问是否继续？[回车, yes, y, 是, ok] \n或者直接输入你的想法:\n')
            if response.lower() in ['', 'yes', 'y', '是', 'ok']:
                return result
            else:
                return self.run(response, return_type, stream_callback, user_check)
        return result
    
    def user_input(self, input, return_type=str, stream_callback=None):
        """
        用户输入
        """
        from GeneralAgent import skills
        if stream_callback is not None:
            self.output_callback = stream_callback
        result = self._run(input, return_type)
        if self.continue_run and self.run_level == 0:
            # 判断是否继续执行
            messages = self.memory.get_messages()
            messages = skills.cut_messages(messages, 2*1000)
            the_prompt = "对于当前状态，无需用户输入或者确认，继续执行任务，请回复yes，其他情况回复no"
            messages += [{'role': 'system', 'content': the_prompt}]
            response = skills.llm_inference(messages, model_type='smart', stream=False)
            if 'yes' in response.lower():
                result = self.run('ok', return_type)
        return result

    def _run(self, input, return_type=str):
        """
        agent run: parse intput -> get llm messages -> run LLM and parse output
        @input: str, user's new input, None means continue to run where it stopped
        @return_type: type, return type, default str
        """
        from GeneralAgent import skills

        result = ''
        def inner_output(token):
            nonlocal result
            if token is not None:
                result += token
            else:
                result += '\n'
            if self.output_callback is None:
                skills.output(token)
            else:
                self.output_callback(token)

        if self.run_level != 0:
            input += '\nPlease don\'t just pass the whole task to agent.run, try to finish part of the task by yourself.\n'
            input += '\n return type should be ' + str(return_type) + '\n'
        self._memory_add_input(input)

        # inner_output(None)
        
        try_count = 0
        while True:
            messages = self._get_llm_messages()
            output_stop = self._llm_and_parse_output(messages, inner_output)
            # logging.info(f'output_stop: {output_stop}')
            if output_stop or self.stop_event.is_set():
                inner_output(None)
                # get python result
                if self.python_run_result is not None:
                    result = self.python_run_result
                    self.python_run_result = None
                # try to transform result to return_type
                if type(result) == str:
                    result = result.strip()
                try:
                    result = return_type(result)
                except Exception as e:
                    pass
                # check return type and try again
                if type(result) != return_type and try_count < 1:
                    logging.info('return type shold be: return_type')
                    try_count += 1
                    self._memory_add_input('return type shold be ' + str(return_type))
                    result = ''
                    continue
                return result

    def _memory_add_input(self, input):
        # 记忆添加用户输入
        self.memory.add_message('user', input)

    
    def _get_llm_messages(self):
        from GeneralAgent import skills
        messages = self.memory.get_messages()
        if self.chat_messages_limit is not None:
            messages = messages[-self.chat_messages_limit:]
        token_limit = skills.get_llm_token_limit(self.model_type)
        messages = skills.cut_messages(messages, int(token_limit*0.8))
        system_prompt = '\n\n'.join([interpreter.prompt(messages) for interpreter in self.interpreters])
        messages = [{'role': 'system', 'content': system_prompt}] + messages
        return messages

    def _llm_and_parse_output(self, messages, output_callback):
        from GeneralAgent import skills
        try:
            result = ''
            is_stop = True
            is_break = False
            response = skills.llm_inference(messages, model_type=self.model_type, stream=True)
            message_id = None
            for token in response:
                if token is None: break
                result += token
                output_callback(token)
                interpreter:Interpreter = None
                for interpreter in self.interpreters:
                    if interpreter.output_match(result):
                        logging.debug('interpreter: ' + interpreter.__class__.__name__)
                        message_id = self.memory.add_message('assistant', result)
                        self.memory.push_stack()
                        output, is_stop = interpreter.output_parse(result)
                        if self.python_run_result is not None:
                            output = output.strip()
                            if len(output) > 50000:
                                output = output[:50000] + '...'
                        self.memory.pop_stack()
                        message_id = self.memory.append_message('assistant', '\n' + output + '\n', message_id=message_id)
                        result = ''
                        if is_stop:
                            output_callback(None)
                            output_callback('```output\n' + output + '\n```\n')
                        is_break = True
                        break
                if is_break:
                    break
            if len(result) > 0:
                message_id = self.memory.add_message('assistant', result)
            return is_stop
        except Exception as e:
            logging.exception(e)
            output_callback(str(e))
            return True
        
    def delete(self):
        """
        删除agent: 删除memory和python序列化文件
        """
        if self._memory_path is not None and os.path.exists(self._memory_path):
            os.remove(self._memory_path)
        if self._python_path is not None and os.path.exists(self._python_path):
            os.remove(self._python_path)