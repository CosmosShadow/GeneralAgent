# Agent
import os, re
import asyncio
import logging
from GeneralAgent.llm import llm_inference
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import PlanInterpreter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, AskInterpreter, FileInterpreter


def default_output_recall(output):
    if output is not None:
        print(output, end='', flush=True)
    else:
        print('\n[output end]\n', end='', flush=True)


class Agent:
    def __init__(self, workspace, input_interpreters=None, output_interpreters=None):
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.memory = Memory(serialize_path=f'{workspace}/memory.json')
        
        self.is_running = False
        self.stop_event = asyncio.Event()

        # input interpreters
        if input_interpreters is not None:
            self.input_interpreters = input_interpreters
        else:
            plan_interperter = PlanInterpreter(self.memory)
            self.input_interpreters = [plan_interperter]

        # output interpreters
        if output_interpreters is not None:
            assert isinstance(output_interpreters, list)
            assert len(output_interpreters) > 0
            # the first interpreter must be RoleInterpreter
            if not isinstance(output_interpreters[0], RoleInterpreter):
                prefix_interpreter = RoleInterpreter()
                self.output_interpreters = [prefix_interpreter] + output_interpreters
            else:
                self.output_interpreters = output_interpreters
        else:
            prefix_interpreter = RoleInterpreter()
            python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
            bash_interpreter = ShellInterpreter('./')
            applescript_interpreter = AppleScriptInterpreter()
            file_interpreter = FileInterpreter('./')
            ask_interpreter = AskInterpreter()
            self.output_interpreters = [prefix_interpreter, python_interpreter, bash_interpreter, applescript_interpreter, file_interpreter, ask_interpreter]

    async def run(self, input=None, for_node_id=None, output_recall=default_output_recall):
        self.is_running = True
        input_node = self._insert_node(input, for_node_id) if input is not None else None

        # input interpreter
        if input_node is not None:
            self.memory.set_current_node(input_node)
            for interpreter in self.input_interpreters:
                match = re.compile(interpreter.match_template, re.DOTALL).search(input_node.content)
                if match is not None:
                    logging.info('interpreter: ' + interpreter.__class__.__name__)
                    interpreter.parse(input_node.content)
                    break

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

    def _insert_node(self, input, for_node_id=None):
        node = MemoryNode(role='user', action='input', content=input)
        if for_node_id is None:
            self.memory.add_node(node)
        else:
            for_node = self.memory.get_node(for_node_id)
            self.memory.add_node_after(for_node, node)
            self.memory.success_node(for_node)
        return node
    
    async def _execute_node(self, node, output_recall):
        # construct system prompt
        messages = self.memory.get_related_messages_for_node(node)
        system_prompt = '\n\n'.join([interpreter.prompt(messages) for interpreter in self.output_interpreters])
        messages = [{'role': 'system', 'content': system_prompt}] + messages
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
            response = llm_inference(messages)
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
            await output_recall(None)
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
            await output_recall(result)
            self.memory.delete_node(answer_node)
            return node, is_stop