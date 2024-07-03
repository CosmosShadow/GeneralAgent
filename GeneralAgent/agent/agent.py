# Agent
import os
import logging
from typing import Union
from GeneralAgent.memory import StackMemory
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.interpreter import KnowledgeInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter


class Agent():
    """
    Agent
    """
    # @memory: Memory
    # @interpreters: list, interpreters
    # @output_callback: function, output_callback(content: str) -> None
    # @python_run_result: str, python run result
    # @run_level: int, python run level, use for check stack overflow level
    # @continue_run: bool, continue run when task not finished
    # @disable_python_run: bool, disable python run
    # @hide_python_code: bool, hide python code in output
    memory = None
    interpreters = []
    output_callback = None
    python_run_result = None
    run_level = 0
    continue_run = True
    disable_python_run = False
    hide_python_code = False

    def __init__(self, 
                 role:str=None, 
                 functions:list=[], 
                 knowledge_files=[],
                 rag_function=None,
                 workspace:str=None, 
                 model=None, 
                 token_limit=None,
                 api_key=None,
                 base_url=None,
                 self_call=False, 
                 continue_run=False,
                 output_callback=None,
                 disable_python_run=False,
                 hide_python_code=False,
                 ):
        """
        @role: str, Agent角色描述，例如"你是一个小说家"，默认为None

        @functions: list, Agent可用的函数(工具)列表，默认为[]

        @knowledge_files: list, 知识库文件列表。当执行delete()函数时，不会删除构建好的知识库(embedding). 

        @rag_function: function, RAG function，用于自定义RAG函数，输入参数为chat模式的messages(包含最近一次输入)，返回值为字符串.

        @workspace: str, Agent序列化目录地址，如果目录不存在会自动创建，如果workspace不为None，则会从workspace中加载序列化的memory和python代码。默认None表示不序列化，不加载。当knowledge_files不为空时, workspace必须提供

        @model: str, 模型类型，比如"gpt-3.5-turbo", "gpt-4o"等

        @token_limit: int, 模型token限制. None: gpt3.5: 16*1000, gpt4: 128*1000, 其他: 16*1000

        @api_key: str,  OpenAI or other LLM API KEY

        @base_url: str, OpenAI or other LLM API BASE URL

        @self_call: bool, 是否开启自我调用(Agent可以写代码来自我调用完成复杂任务), 默认为False.

        @continue_run: bool, 是否自动继续执行。Agent在任务没有完成时，是否自动执行。默认为True.

        @output_callback: function, 输出回调函数，用于输出Agent的流式输出结果，默认为None，表示使用默认输出函数(skills.output==print)

        @disable_python_run: bool, 是否禁用python运行，默认为False

        @hide_python_code: bool, 是否隐藏python代码，默认为False

        """
        from GeneralAgent import skills
        if workspace is None and len(knowledge_files) > 0:
            raise Exception('workspace must be provided when knowledge_files is not empty')
        if workspace is not None and not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace
        self.disable_python_run = disable_python_run
        self.hide_python_code = hide_python_code
        self.memory = StackMemory(serialize_path=self._memory_path)
        self.role_interpreter = RoleInterpreter(role=role, self_call=self_call)
        self.python_interpreter = PythonInterpreter(self, serialize_path=self._python_path)
        self.python_interpreter.function_tools = functions
        self.model = model or os.environ.get('DEFAULT_LLM_MODEL', 'gpt-4o')
        self.token_limit = token_limit or skills.get_llm_token_limit(self.model)
        self.api_key = api_key
        self.base_url = base_url
        self.continue_run = continue_run
        self.knowledge_interpreter = KnowledgeInterperter(workspace, knowledge_files=knowledge_files, rag_function=rag_function)
        self.interpreters = [self.role_interpreter, self.python_interpreter, self.knowledge_interpreter]
        if output_callback is not None:
            self.output_callback = output_callback
        else:
            # 默认输出回调函数
            from GeneralAgent import skills
            self.output_callback = skills.output

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

    def disable_output_callback(self):
        """
        禁用输出回调函数
        """
        self.tmp_output_callback = self.output_callback
        self.output_callback = None

    def enable_output_callback(self):
        """
        启用输出回调函数
        """
        self.output_callback = self.tmp_output_callback
        self.tmp_output_callback = None

    def disable_python(self):
        """
        禁用python运行
        """
        self.disable_python_run = True

    def enable_python(self):
        """
        启用python运行
        """
        self.disable_python_run = False

    def run(self, command:Union[str, list], return_type=str, show_stream=True, user_check=False, check_render=None):
        """
        执行command命令，并返回return_type类型的结果

        @command: 命令内容, str or list. list: [{'type': 'text', 'text': 'hello world'}, {'type': 'image_url', 'image_url': 'xxxx.jpg'}]

        @return_type: type, 返回类型，默认str. 可以是任意的python类型。

        @show_stream: bool, 是否显示流输出

        @user_check: bool, 是否需要用户确认命令执行后的结果，默认不需要

        @check_render: function, 检查渲染函数，用于渲染显示给用户的check内容: check_render(result:return_type) -> str

        """
        # 代码调用agent执行，直接run_level+1
        self.run_level += 1
        if not show_stream:
            self.disable_output_callback()
        try:
            from GeneralAgent import skills
            result = self._run(command, return_type)
            if user_check:
                # 没有渲染函数 & 没有输出回调函数: 用户不知道确认什么内容，则默认是str(result)
                if check_render is None:
                    if self.output_callback is None:
                        show = str(result)
                    else:
                        show = ' '
                else:
                    show = check_render(result)
                response = skills.check(show)
                if response is None:
                    return result
                else:
                    return self.run(response, return_type, user_check=user_check, check_render=check_render)
            return result
        except Exception as e:
            logging.exception(e)
            return str(e)
        finally:
            self.run_level -= 1
            if not show_stream:
                self.enable_output_callback()

    
    def user_input(self, input:Union[str, list]):
        """
        Agent接收用户输入
        
        :input: 用户输入内容, str类型 or list: [{'type': 'text', 'text': 'hello world'}, {'type': 'image_url', 'image_url': 'xxxx.jpg'}]
        """
        from GeneralAgent import skills
        result = self._run(input)
        if self.continue_run and self.run_level == 0:
            # 判断是否继续执行
            messages = self.memory.get_messages()
            messages = skills.cut_messages(messages, 2*1000)
            the_prompt = "对于当前状态，无需用户输入或者确认，继续执行任务，请回复yes，其他情况回复no"
            messages += [{'role': 'system', 'content': the_prompt}]
            response = skills.llm_inference(messages, model='smart', stream=False, api_key=self.api_key, base_url=self.base_url)
            if 'yes' in response.lower():
                result = self.run('ok')
        return result

    def _run(self, input, return_type=str):
        """
        agent run: parse intput -> get llm messages -> run LLM and parse output

        @input: str, user's new input, None means continue to run where it stopped

        @return_type: type, return type, default str
        """
        from GeneralAgent import skills

        result = ''
        def local_output(token):
            nonlocal result
            if token is not None:
                result += token
            else:
                result += '\n'
            if self.output_callback is not None:
                self.output_callback(token)

        if self.run_level != 0:
            if return_type == str:
                # add_content = '\n Return type should be ' + str(return_type) + '\n'
                add_content = ''
            else:
                add_content = '\n Return type should be ' + str(return_type) + ' in Python Code\n'
            if isinstance(input, list):
                input += [add_content]
            else:
                input += add_content
        self._memory_add_input(input)
        
        try_count = 0
        while True:
            messages = self._get_llm_messages()
            output_stop = self._llm_and_parse_output(messages, local_output)
            if output_stop:
                local_output(None)
                if self.python_run_result is not None:
                    result = self.python_run_result
                    self.python_run_result = None
                if type(result) == str:
                    result = result.strip()
                # 不再转换了，因为会把字符串转成列表，结果不符合预期
                # try:
                #     result = return_type(result)
                # except Exception as e:
                #     pass
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
        # 获取记忆 + prompt
        messages = self.memory.get_messages()
        if self.disable_python_run:
            prompt = '\n\n'.join([interpreter.prompt(messages) for interpreter in self.interpreters if interpreter != self.python_interpreter])
        else:
            prompt = '\n\n'.join([interpreter.prompt(messages) for interpreter in self.interpreters])
        # 动态调整记忆长度
        prompt_count = skills.string_token_count(prompt)
        left_count = int(self.token_limit * 0.9) - prompt_count
        messages = skills.cut_messages(messages, left_count)
        # 组合messages
        messages = [{'role': 'system', 'content': prompt}] + messages
        return messages

    def _llm_and_parse_output(self, messages, output_callback):
        outputer = _PythonCodeFilter(output_callback, self.hide_python_code)
        from GeneralAgent import skills
        try:
            result = ''
            is_stop = True
            is_break = False
            response = skills.llm_inference(messages, model=self.model, stream=True, api_key=self.api_key, base_url=self.base_url)
            message_id = None
            for token in response:
                if token is None: break
                result += token
                outputer.process_text(token)
                interpreter:Interpreter = None
                for interpreter in self.interpreters:
                    if self.disable_python_run and interpreter == self.python_interpreter:
                        continue
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
                        # if is_stop:
                        outputer.process_text(None)
                        outputer.process_text('```output\n' + output + '\n```\n')
                        if interpreter == self.python_interpreter:
                            outputer.exit_python_code()
                        is_break = True
                        break
                if is_break:
                    break
            if len(result) > 0:
                message_id = self.memory.add_message('assistant', result)
            outputer.flush()
            return is_stop
        except Exception as e:
            logging.exception(e)
            outputer.process_text(str(e))
            outputer.flush()
            return True
        
    def clear(self):
        """
        清除: 删除memory和python序列化文件。不会删除workspace和知识库。
        """
        if self._memory_path is not None and os.path.exists(self._memory_path):
            os.remove(self._memory_path)
        if self._python_path is not None and os.path.exists(self._python_path):
            os.remove(self._python_path)
        self.memory = StackMemory(serialize_path=self._memory_path)
        self.python_interpreter = PythonInterpreter(self, serialize_path=self._python_path)


class _PythonCodeFilter():
    """
    Python代码过滤器，用于隐藏Python代码块
    """
    def __init__(self, output_callback, hide_python_code):
        """
        构造函数

        @output_callback: 输出回调函数

        @hide_python_code: 是否隐藏python代码, bool
        """
        self.hide_python_code = hide_python_code
        self.in_python_code = False
        self.buffer = ''
        self.output_callback = output_callback

    def process_text(self, text):
        """
        处理输入问题
        """
        if not self.hide_python_code:
            self.output_callback(text)
        else:
            if text is None:
                self.flush()
                self.output_callback(None)
            else:
                if not self.in_python_code:
                    self.buffer += text
                    self._process_buffer()

    def exit_python_code(self):
        """
        退出python代码块
        """
        self.in_python_code = False

    def _process_buffer(self):
        if self.buffer.endswith('```python'):
            self.in_python_code = True
            self.buffer = ''  # 清空缓冲区，因为我们不打印```python
        elif self.buffer.endswith('```') and not self.in_python_code:
            if self.buffer[:-3]:  # 如果```前有其他文本，先打印出来
                self.output_callback(self.buffer[:-3])
            self.buffer = '```'  # 重置缓冲区为```，以便检查后续是否为python代码块
        else:
            self.output_callback(self.buffer)
            self.buffer = ''

    def flush(self):
        if self.buffer:
            self.output_callback(self.buffer)
            self.buffer = ''