# Agent
import os, re
import asyncio
import logging
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import PlanInterpreter, EmbeddingRetrieveInterperter, LinkRetrieveInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, FileInterpreter
from .abs_agent import AbsAgent


class StackAgent(AbsAgent):

    @classmethod
    def default(cls, workspace):
        # memory
        agent = cls(workspace)
        agent.memory = Memory(serialize_path=f'{workspace}/memory.json')
        # input interpreter
        plan_interperter = PlanInterpreter(agent.memory)
        retrieve_interpreter = EmbeddingRetrieveInterperter(serialize_path=f'{workspace}/read_interperter/')
        agent.input_interpreters = [plan_interperter, retrieve_interpreter]
        # retrieve interpreter
        agent.retrieve_interpreters = [retrieve_interpreter]
        # output interpreter
        role_interpreter = RoleInterpreter()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        file_interpreter = FileInterpreter()
        agent.output_interpreters = [role_interpreter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter]
        return agent
    
    @classmethod
    def empty(cls, workspace):
        """
        empty agent, only role interpreter and memory, work like a basic LLM chatbot
        """
        agent = cls(workspace)
        agent.memory = Memory(serialize_path=f'{workspace}/memory.json')
        agent.output_interpreters = [RoleInterpreter()]
        return agent

    @classmethod
    def with_functions(cls, functions, role_prompt=None, workspace = './', model_type='smart'):
        """
        functions: list, [function1, function2, ...]
        role_prompt: str, role prompt
        workspace: str, workspace path
        import_code: str, import code
        libs: str, libs
        """
        agent = cls(workspace)
        agent.memory = Memory(serialize_path=f'{workspace}/memory.json')
        role_interpreter = RoleInterpreter(system_prompt=role_prompt)
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = functions
        agent.output_interpreters = [role_interpreter, python_interpreter]
        agent.model_type = model_type
        return agent
    
    @classmethod
    def with_link_memory(cls, workspace):
        agent = cls(workspace)
        link_memory_interpreter = LinkRetrieveInterperter(python_interpreter)
        prompt_append = link_memory_interpreter.get_python_access_prompt()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin', prompt_append=prompt_append)
        # memory
        agent.memory = Memory(serialize_path=f'{workspace}/memory.json')
        # input interpreter
        plan_interperter = PlanInterpreter(agent.memory)
        agent.input_interpreters = [plan_interperter, link_memory_interpreter]
        # retrieve interpreter
        agent.retrieve_interpreters = [link_memory_interpreter]
        # output interpreter
        role_interpreter = RoleInterpreter()
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        file_interpreter = FileInterpreter()
        agent.output_interpreters = [role_interpreter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter]
        # 
        return agent
    
    async def run(self, input=None, input_for_memory_node_id=-1, output_callback=default_output_callback):
        """
        input: str, user's new input, None means continue to run where it stopped
        input_for_memory_node_id: int, -1 means input is not from memory, None means input new, otherwise input is for memory node
        output_callback: async function, output_callback(content: str) -> None
        """
        if input_for_memory_node_id == -1:
            memory_node_id = self.memory.current_node.node_id if self.memory.current_node is not None else None
        else:
            memory_node_id = input_for_memory_node_id
        self.is_running = True
        input_node = self._insert_node(input, memory_node_id) if input is not None else None

        # input interpreter
        if input_node is not None:
            input_content = input
            input_stop = False
            self.memory.set_current_node(input_node)
            for interpreter in self.input_interpreters:
                if interpreter.match(input_content):
                    logging.info('interpreter: ' + interpreter.__class__.__name__)
                    # await output_callback('input parsing\n')
                    input_content, case_is_stop = await interpreter.parse(input_content)
                    if case_is_stop:
                        input_stop = True
            input_node.content = input_content
            self.memory.update_node(input_node)
            if input_stop:
                await output_callback(input_content)
                await output_callback(None)
                await asyncio.sleep(1)
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
        node = MemoryNode(role='user', action='input', content=input)
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
        system_prompt = '\n\n'.join([await interpreter.prompt(messages) for interpreter in self.output_interpreters])
        retrieve_prompt = '\n\n'.join([await interpreter.prompt(messages) for interpreter in self.retrieve_interpreters])
        all_messages = [{'role': 'system', 'content': system_prompt}]
        if len(retrieve_prompt.strip()) > 0:
            all_messages.append({'role': 'system', 'content': 'Background information: \n' + retrieve_prompt})
        all_messages += messages
        if skills.messages_token_count(all_messages) > 3000:
            all_messages = skills.cut_messages(all_messages, 3000)
        # add answer node and set current node
        answer_node = MemoryNode(role='system', action='answer', content='')
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
            response = skills.llm_inference(all_messages, model_type=self.model_type, stream=True)
            for token in response:
                if token is None: break
                result += token
                # print(token)
                if self.hide_output_parse:
                    if not in_parse_content:
                        for interpreter in self.output_interpreters:
                            is_start_matched, string_matched = interpreter.match_start(result)
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
                for interpreter in self.output_interpreters:
                    if interpreter.match(result):
                        logging.info('interpreter: ' + interpreter.__class__.__name__)
                        output, is_stop = await interpreter.parse(result)
                        result += output.strip()
                        if not self.hide_output_parse or is_stop:
                            await output_callback(output.strip())
                        is_break = True
                        in_parse_content = False
                        if self.hide_output_parse:
                            is_matched, string_left = interpreter.match_end(result)
                            output_callback(string_left)
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