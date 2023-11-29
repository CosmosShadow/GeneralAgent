# Agent
import os, re
import asyncio
import logging
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.memory import StackMemory, StackMemoryNode
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.interpreter import PlanInterpreter, EmbeddingRetrieveInterperter, LinkRetrieveInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, FileInterpreter
from .abs_agent import AbsAgent


class StackAgent(AbsAgent):

    def __init__(self, workspace='./'):
        super().__init__(workspace)
        self.memory = StackMemory(serialize_path=f'{workspace}/memory.json')

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
        plan_interperter = PlanInterpreter(agent.memory)
        if retrieve_type == 'embedding':
            retrieve_interperter = EmbeddingRetrieveInterperter(serialize_path=f'{workspace}/read_interperter/')
        else:
            retrieve_interperter = LinkRetrieveInterperter(python_interpreter)
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        file_interpreter = FileInterpreter()
        agent.interpreters = [role_interpreter, plan_interperter, retrieve_interperter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter]
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
        role_interpreter = RoleInterpreter(system_prompt=role_prompt)
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = functions
        agent.interpreters = [role_interpreter, python_interpreter, ShellInterpreter()]
        agent.model_type = model_type
        return agent

    
    async def run(self, input=None, output_callback=default_output_callback, input_for_memory_node_id=-1):
        """
        agent run: parse intput -> get llm messages -> run LLM and parse output
        input: str, user's new input, None means continue to run where it stopped
        input_for_memory_node_id: int, -1 means input is not from memory, None means input new, otherwise input is for memory node
        output_callback: async function, output_callback(content: str) -> None
        """
        self.is_running = True
        
        if input_for_memory_node_id == -1:
            memory_node_id = self.memory.current_node.node_id if self.memory.current_node is not None else None
        else:
            memory_node_id = input_for_memory_node_id
        input_node = self._insert_node(input, memory_node_id) if input is not None else None

        # input interpreter
        if input_node is not None:
            input_content = input
            input_stop = False
            self.memory.set_current_node(input_node)
            interpreter:Interpreter = None
            for interpreter in self.interpreters:
                if interpreter.input_match(input_content):
                    logging.info('interpreter: ' + interpreter.__class__.__name__)
                    # await output_callback('input parsing\n')
                    input_content, case_is_stop = await interpreter.input_parse(input_content)
                    if case_is_stop:
                        await output_callback(input_content)
                        input_stop = True
            input_node.content = input_content
            self.memory.update_node(input_node)
            if input_stop:
                self.memory.success_node(input_node)
                self.is_running = False
                return input_node.node_id

        # execute todo node from memory
        todo_node = self.memory.get_todo_node() or input_node
        logging.debug(self.memory)
        while todo_node is not None:
            new_node, is_stop = await self._execute_node(todo_node, output_callback)
            logging.debug(self.memory)
            logging.debug(new_node)
            logging.debug(is_stop)
            if is_stop:
                return new_node.node_id
            todo_node = self.memory.get_todo_node()
            await asyncio.sleep(0)
            if self.stop_event.is_set():
                self.is_running = False
                return None
        self.is_running = False
        return None

    def _insert_node(self, input, memory_node_id=None):
        node = StackMemoryNode(role='user', action='input', content=input)
        if memory_node_id is None:
            logging.debug(self.memory)
            self.memory.add_node(node)
        else:
            for_node = self.memory.get_node(memory_node_id)
            self.memory.add_node_after(for_node, node)
            self.memory.success_node(for_node)
        return node
    
    async def _execute_node(self, node, output_callback):
        # construct system prompt
        from GeneralAgent import skills
        messages = self.memory.get_related_messages_for_node(node)
        messages = skills.cut_messages(messages, 3000)
        system_prompt = '\n\n'.join([await interpreter.prompt(messages) for interpreter in self.interpreters])
        messages = [{'role': 'system', 'content': system_prompt}] + messages

        # add answer node and set current node
        answer_node = StackMemoryNode(role='system', action='answer', content='')
        self.memory.add_node_after(node, answer_node)
        self.memory.set_current_node(answer_node)

        if node.action == 'plan':
            await output_callback(f'\n[{node.content}]\n')

        try:
            result = ''
            is_stop = False
            is_break = False
            in_parse_content = False
            cache_tokens = []
            response = skills.llm_inference(messages, model_type=self.model_type, stream=True)
            for token in response:
                if token is None: break
                result += token
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
                        result += '\n' + output.strip() + '\n'
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
            # await output_callback('\n')
            # update current node and answer node
            answer_node.content = result
            self.memory.update_node(answer_node)
            self.memory.success_node(node)
            # llm run end with any interpreter, success the node
            if not is_break:
                self.memory.success_node(answer_node)
            return answer_node, is_stop
        except Exception as e:
            # if fail, recover
            logging.exception(e)
            await output_callback(str(e))
            self.memory.delete_node(answer_node)
            self.memory.set_current_node(node)
            return node, True