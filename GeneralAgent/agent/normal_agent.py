# Agent
import os, re
import asyncio
import logging
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.memory import NormalMemory
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.interpreter import EmbeddingRetrieveInterperter, LinkRetrieveInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, FileInterpreter
from .abs_agent import AbsAgent


class NormalAgent(AbsAgent):

    def __init__(self, workspace='./'):
        super().__init__(workspace)
        self.memory = NormalMemory(serialize_path=f'{workspace}/normal_memory.json')

    @classmethod
    def empty(cls, workspace='./'):
        """
        empty agent, only role interpreter and memory, work like a basic LLM chatbot
        """
        agent = cls(workspace)
        agent.interpreters = [RoleInterpreter()]
        return agent

    @classmethod
    def default(cls, workspace='./', retrieve_type='embedding'):
        """
        default agent, with all interpreters
        @workspace: str, workspace path
        @retrieve_type: str, 'embedding' or 'link'
        """
        agent = cls(workspace)
        # memory
        # interpreters
        role_interpreter = RoleInterpreter()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        if retrieve_type == 'embedding':
            retrieve_interperter = EmbeddingRetrieveInterperter(serialize_path=f'{workspace}/read_interperter/')
        else:
            retrieve_interperter = LinkRetrieveInterperter(python_interpreter)
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        file_interpreter = FileInterpreter()
        agent.interpreters = [role_interpreter, retrieve_interperter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter]
        return agent

    @classmethod
    def with_functions(cls, functions, role_prompt=None, workspace = './', model_type='smart'):
        """
        functions: list, [function1, function2, ...]
        @role_prompt: str, role prompt
        @workspace: str, workspace path
        @import_code: str, import code
        @libs: str, libs
        """
        agent = cls(workspace)
        role_interpreter = RoleInterpreter()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = functions
        agent.interpreters = [role_interpreter, python_interpreter, ShellInterpreter()]
        agent.model_type = model_type
        if role_prompt is not None:
            agent.add_role_prompt(role_prompt)
        return agent

    
    async def run(self, input=None, output_callback=default_output_callback, input_for_memory_node_id=-1):
        """
        agent run: parse intput -> get llm messages -> run LLM and parse output
        @input: str, user's new input, None means continue to run where it stopped
        @input_for_memory_node_id: int, -1 means input is not from memory, None means input new, otherwise input is for memory node
        @output_callback: async function, output_callback(content: str) -> None
        """
        self.is_running = True

        input_stop = await self._parse_input(input, output_callback)
        if input_stop:
            self.is_running = False
            return

        while True:
            messages = await self._get_llm_messages()
            output_stop = await self._llm_and_parse_output(messages, output_callback)
            if output_stop:
                self.is_running = False
                return
            await asyncio.sleep(0)
            if self.stop_event.is_set():
                self.is_running = False
                return

    async def _parse_input(self, input, output_callback):
        self.memory.add_message('user', input)
        input_content = input
        input_stop = False
        interpreter:Interpreter = None
        for interpreter in self.interpreters:
            if interpreter.input_match(input_content):
                logging.info('interpreter: ' + interpreter.__class__.__name__)
                parse_output, case_is_stop = await interpreter.input_parse(input_content)
                if case_is_stop:
                    await output_callback(parse_output)
                    input_stop = True
        return input_stop
    
    async def _get_llm_messages(self):
        from GeneralAgent import skills
        messages = self.memory.get_messages()
        token_limit = skills.get_llm_token_limit(self.model_type)
        messages = skills.cut_messages(messages, int(token_limit*0.8))
        system_prompt = '\n\n'.join([await interpreter.prompt(messages) for interpreter in self.interpreters])
        messages = [{'role': 'system', 'content': system_prompt}] + messages
        return messages

    async def _llm_and_parse_output(self, messages, output_callback):
        from GeneralAgent import skills
        try:
            result = ''
            is_stop = True
            is_break = False
            in_parse_content = False
            cache_tokens = []
            response = skills.llm_inference(messages, model_type=self.model_type, stream=True)
            for token in response:
                if token is None: break
                result += token
                # logging.debug(result)
                # print(token)
                if self.hide_output_parse:
                    if not in_parse_content:
                        interpreter:Interpreter = None
                        for interpreter in self.interpreters:
                            is_start_matched, string_matched = interpreter.output_match_start(result)
                            if is_start_matched:
                                in_parse_content = True
                                # clear cache
                                cache_tokens.append(token)
                                left_count = len(string_matched)
                                while left_count > 0:
                                    left_count -= len(cache_tokens[-1])
                                    cache_tokens.remove(cache_tokens[-1])
                                while len(cache_tokens) > 0:
                                    pop_token = cache_tokens.pop(0)
                                    await output_callback(pop_token)
                        if not in_parse_content:
                            # cache token
                            cache_tokens.append(token)
                            if len(cache_tokens) > 5:
                                pop_token = cache_tokens.pop(0)
                                await output_callback(pop_token)
                else:
                    await output_callback(token)
                interpreter:Interpreter = None
                for interpreter in self.interpreters:
                    if interpreter.output_match(result):
                        logging.info('interpreter: ' + interpreter.__class__.__name__)
                        output, is_stop = await interpreter.output_parse(result)
                        if interpreter.outptu_parse_done_recall is not None:
                            await interpreter.outptu_parse_done_recall()
                        if self.hide_output_parse:
                            is_matched, string_left = interpreter.output_match_end(result)
                            await output_callback(string_left)
                        while len(cache_tokens) > 0:
                            pop_token = cache_tokens.pop(0)
                            await output_callback(pop_token)
                        result += '\n' + output.strip() + '\n'
                        # logging.debug(result)
                        if not self.hide_output_parse or is_stop:
                            await output_callback('\n' + output.strip() + '\n')
                        is_break = True
                        in_parse_content = False
                        break
                if is_break:
                    break
            while len(cache_tokens) > 0:
                pop_token = cache_tokens.pop(0)
                await output_callback(pop_token)
            # append messages
            # logging.debug(result)
            self.memory.append_message('assistant', result)
            return is_stop
        except Exception as e:
            # if fail, recover
            logging.exception(e)
            await output_callback(str(e))
            return True