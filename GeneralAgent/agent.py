# Agent
import os, re
import asyncio
import logging
from GeneralAgent.utils import default_get_input, default_output_recall
from GeneralAgent.llm import llm_inference
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import PlanInterpreter, RetrieveInterpreter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, AskInterpreter, FileInterpreter


class Agent:
    def __init__(self, 
                 workspace='./',
                 memory=None,
                 input_interpreters=[],
                 output_interpreters=[],
                 retrieve_interpreters=[]
                 ):
        self.is_running = False
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
        
        # the first must be role interpreter
        if len(output_interpreters) > 0:
            if not isinstance(output_interpreters[0], RoleInterpreter):
                self.output_interpreters.insert(0, RoleInterpreter())

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

    def information(self):
        # describe input、output、retrieve interpreters
        pass

    async def run(self, input=None, input_for_memory_node_id=-1, output_recall=default_output_recall):
        """
        input: str, user's new input, None means continue to run where it stopped
        input_for_memory_node_id: int, -1 means input is not from memory, None means input new, otherwise input is for memory node
        output_recall: async function, output_recall(content: str) -> None
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
                match = re.compile(interpreter.match_template, re.DOTALL).search(input_content)
                if match is not None:
                    logging.info('interpreter: ' + interpreter.__class__.__name__)
                    input_content, case_is_stop = interpreter.parse(input_content)
                    if case_is_stop:
                        input_stop = True
            input_node.content = input_content
            self.memory.update_node(input_node)
            if input_stop:
                await output_recall(input_content)
                self.memory.success_node(input_node)
                self.is_running = False
                return input_node.node_id

        # execute todo node from memory
        todo_node = self.memory.get_todo_node() or input_node
        logging.debug(self.memory)
        while todo_node is not None:
            new_node, is_stop = await self._execute_node(todo_node, output_recall)
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
    
    async def _execute_node(self, node, output_recall):
        # construct system prompt
        messages = self.memory.get_related_messages_for_node(node)
        system_prompt = '\n\n'.join([interpreter.prompt(messages) for interpreter in self.output_interpreters])
        retrieve_prompt = '\n\n'.join([interpreter.prompt(messages) for interpreter in self.retrieve_interpreters])
        all_messages = [{'role': 'system', 'content': system_prompt}]
        if len(retrieve_prompt.strip()) > 0:
            all_messages.append({'role': 'system', 'content': 'Background information: \n' + retrieve_prompt})
        all_messages += messages
        # TODO: when messages exceed limit, cut it
        # add answer node and set current node
        answer_node = MemoryNode(role='system', action='answer', content='')
        self.memory.add_node_after(node, answer_node)
        self.memory.set_current_node(answer_node)

        if node.action == 'plan':
            await output_recall(f'\n[{node.content}]\n')

        try:
            result = ''
            is_stop = False
            is_break = False
            response = llm_inference(all_messages)
            for token in response:
                if token is None: break
                result += token
                await output_recall(token)
                for interpreter in self.output_interpreters:
                    if interpreter.match(result):
                        logging.info('interpreter: ' + interpreter.__class__.__name__)
                        output, is_stop = interpreter.parse(result)
                        result += '\n' + output.strip() + '\n'
                        await output_recall('\n' + output + '\n')
                        is_break = True
                        break
                if is_break:
                    break
            await output_recall('\n')
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
            await output_recall(str(e))
            self.memory.delete_node(answer_node)
            self.memory.set_current_node(node)
            return node, True