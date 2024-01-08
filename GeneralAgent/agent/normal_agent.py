# Agent
import logging
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.memory import NormalMemory, StackMemory
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.interpreter import EmbeddingRetrieveInterperter, LinkRetrieveInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, FileInterpreter
from .abs_agent import AbsAgent


class NormalAgent(AbsAgent):

    def __init__(self, workspace='./'):
        super().__init__(workspace)
        # self.memory = NormalMemory(serialize_path=f'{workspace}/normal_memory.json')
        self.memory = StackMemory(serialize_path=f'{workspace}/normal_memory.json')

    # def save(self):
    #     for interpreter in self.interpreters:
    #         if interpreter.__class__.__name__ == 'PythonInterpreter':
    #             interpreter.save()

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
        python_interpreter = PythonInterpreter(agent, serialize_path=f'{workspace}/code.bin')
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
    def with_functions(cls, functions, role_prompt=None, workspace = './', model_type='smart', variables=None):
        """
        agent with functions
        @functions: list, [function1, function2, ...]
        @role_prompt: str, role prompt
        @workspace: str, workspace path
        @model_type: str, 'smart', 'normal', or 'long'
        @variables: dict, embed variables to python interpreter, like {'a': a, 'variable_name': variable_value}, then Agent can use the variables in python interpreter like `variable_name`
        """
        agent = cls(workspace)
        role_interpreter = RoleInterpreter()
        python_interpreter = PythonInterpreter(agent, serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = functions
        agent.interpreters = [role_interpreter, python_interpreter]
        agent.model_type = model_type
        if role_prompt is not None:
            agent.add_role_prompt(role_prompt)
        if variables is not None:
            for key, value in variables.items():
                python_interpreter.set_variable(key, value)
        return agent


    def run(self, input, return_type=str, stream_callback=None):
        """
        agent run: parse intput -> get llm messages -> run LLM and parse output
        @input: str, user's new input, None means continue to run where it stopped
        @return_type: type, return type, default str
        @stream_callback: stream callback function, use for stream output
        """
        self.is_running = True

        if stream_callback is not None:
            self.output_callback = stream_callback

        result = ''
        def inner_output(token):
            nonlocal result
            if token is not None:
                result += token
            else:
                result += '\n'
            if self.output_callback is None:
                default_output_callback(token)
            else:
                self.output_callback(token)

        inner_output(' ')

        if self.run_level != 0:
            input += '\nPlease don\'t just pass the whole task to agent.run, try to finish part of the task by yourself.\n'
            input += '\n return type should be ' + str(return_type) + '\n'
        input_stop = self._parse_input(input, inner_output)
        if input_stop:
            self.is_running = False
            return result

        inner_output(None)
        
        try_count = 0
        while True:
            messages = self._get_llm_messages()
            output_stop = self._llm_and_parse_output(messages, inner_output)
            if output_stop or self.stop_event.is_set():
                inner_output(None)
                self.is_running = False
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
                    try_count += 1
                    input_stop = self._parse_input('return type shold be ' + str(return_type), inner_output)
                    result = ''
                    continue
                return result

    def _parse_input(self, input, output_callback):
        self.memory.add_message('user', input)
        input_content = input
        input_stop = False
        interpreter:Interpreter = None
        for interpreter in self.interpreters:
            if interpreter.input_match(input_content):
                logging.info('interpreter: ' + interpreter.__class__.__name__)
                parse_output, case_is_stop = interpreter.input_parse(input_content)
                if case_is_stop:
                    output_callback(parse_output)
                    input_stop = True
        return input_stop
    
    def _get_llm_messages(self):
        from GeneralAgent import skills
        messages = self.memory.get_messages()
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
                        logging.info('interpreter: ' + interpreter.__class__.__name__)
                        message_id = self.memory.add_message('assistant', result)
                        self.memory.push_stack()
                        output, is_stop = interpreter.output_parse(result)
                        if interpreter.outptu_parse_done_recall is not None:
                            interpreter.outptu_parse_done_recall()
                        if self.python_run_result is not None:
                            output = output.strip()
                            if len(output) > 5000:
                                output = output[:5000] + '...'
                        self.memory.pop_stack()
                        message_id = self.memory.append_message('assistant', '\n' + output + '\n', message_id=message_id)
                        result = ''
                        if not self.hide_output_parse or is_stop:
                            output_callback(None)
                            output_callback('\n' + output + '\n')
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