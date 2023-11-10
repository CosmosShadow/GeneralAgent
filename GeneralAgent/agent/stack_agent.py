# Agent
import os, re
import asyncio
import logging
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import PlanInterpreter, RetrieveInterpreter, LinkMemoryInterpreter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, AskInterpreter, FileInterpreter
from GeneralAgent.utils import set_logging_level
set_logging_level()

class Agent:
    def __init__(self, 
                 workspace='./',
                 memory=None,
                 input_interpreters=[],
                 output_interpreters=[],
                 retrieve_interpreters=[],
                 model_type='normal'
                 ):
        self.is_running = False
        self.model_type = model_type
        self.stop_event = asyncio.Event()

        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
        while not OPENAI_API_KEY.startswith('sk-'):
            print('enviroment variable OPENAI_API_KEY is not set correctly')
            OPENAI_API_KEY = input('input your openai api key please >>> ')
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
        self.memory = memory or Memory(serialize_path=f'{workspace}/memory.json')
        self.input_interpreters = input_interpreters
        self.retrieve_interpreters = retrieve_interpreters
        self.output_interpreters = output_interpreters
        
        # # the first must be role interpreter
        # if len(output_interpreters) > 0:
        #     if not isinstance(output_interpreters[0], RoleInterpreter):
        #         self.output_interpreters.insert(0, RoleInterpreter())

    @classmethod
    def default(cls, workspace):
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        # memory
        memory = Memory(serialize_path=f'{workspace}/memory.json')
        # input interpreter
        plan_interperter = PlanInterpreter(memory)
        retrieve_interpreter = RetrieveInterpreter(serialize_path=f'{workspace}/read_interperter/')
        input_interpreters = [plan_interperter, retrieve_interpreter]
        # retrieve interpreter
        retrieve_interpreters = [retrieve_interpreter]
        # output interpreter
        role_interpreter = RoleInterpreter()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        file_interpreter = FileInterpreter()
        ask_interpreter = AskInterpreter()
        output_interpreters = [role_interpreter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter, ask_interpreter]
        # 
        return cls(workspace, memory, input_interpreters, output_interpreters, retrieve_interpreters)
    
    @classmethod
    def with_link_memory(cls, workspace, model_type='normal'):
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        variable_name = 'sparks'
        prompt_append = f"""
你可以通过字典{variable_name}访问所有文档中出现<<key>>的值，比如<<Hello world>>:
```
print({variable_name}['Hello world'])
```
"""
        prompt_append = f"""
You can access the values of <<key>> in all documents through the dictionary {variable_name}, such as <<Hello world>>:
```
print({variable_name}['Hello world'])
```
"""
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin', prompt_append=prompt_append)
        # memory
        memory = Memory(serialize_path=f'{workspace}/memory.json')
        # input interpreter
        plan_interperter = PlanInterpreter(memory)
        link_memory_interpreter = LinkMemoryInterpreter(python_interpreter, sparks_dict_name=variable_name)
        input_interpreters = [plan_interperter, link_memory_interpreter]
        # retrieve interpreter
        retrieve_interpreters = [link_memory_interpreter]
        # output interpreter
        role_interpreter = RoleInterpreter()
        bash_interpreter = ShellInterpreter(workspace)
        applescript_interpreter = AppleScriptInterpreter()
        file_interpreter = FileInterpreter()
        ask_interpreter = AskInterpreter()
        output_interpreters = [role_interpreter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter, ask_interpreter]
        # 
        return cls(workspace, memory, input_interpreters, output_interpreters, retrieve_interpreters, model_type=model_type)
    
    @classmethod
    def empty(cls, workspace):
        """
        empty agent, only role interpreter and memory, work like a basic LLM chatbot
        """
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        memory = Memory(serialize_path=f'{workspace}/memory.json')
        input_interpreters = []
        retrieve_interpreters = []
        output_interpreters = [RoleInterpreter()]
        return cls(workspace, memory, input_interpreters, output_interpreters, retrieve_interpreters)
    
    
    @classmethod
    def agent_with_functions(cls, functions, role_prompt=None, workspace = './', import_code=None, libs=None):
        """
        functions: list, [function1, function2, ...]
        role_prompt: str, role prompt
        workspace: str, workspace path
        import_code: str, import code
        libs: str, libs
        """
        from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter
        from GeneralAgent.agent import Agent
        role_interpreter = RoleInterpreter(system_prompt=role_prompt)
        python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin', libs=libs, import_code=import_code)
        python_interpreter.async_tools = functions
        output_interpreters = [role_interpreter, python_interpreter]
        agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')
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
    
    def stop(self):
        self.stop_event.set()

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
            response = skills.llm_inference(all_messages, model_type=self.model_type, stream=True)
            for token in response:
                if token is None: break
                result += token
                await output_callback(token)
                for interpreter in self.output_interpreters:
                    if interpreter.match(result):
                        logging.info('interpreter: ' + interpreter.__class__.__name__)
                        output, is_stop = await interpreter.parse(result)
                        result += '\n' + output.strip() + '\n'
                        await output_callback('\n' + output + '\n')
                        is_break = True
                        break
                if is_break:
                    break
            await output_callback('\n')
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