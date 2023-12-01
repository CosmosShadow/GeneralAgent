import abc
import os
import asyncio
from GeneralAgent.utils import default_get_input, default_output_callback


class AbsAgent(metaclass=abc.ABCMeta):
    """
    Abstract Agent
    @memory: Memory
    @interpreters: list, interpreters
    @model_type: str, 'normal' or 'smart' or 'long'. For OpenAI api, normal=gpt3.5, smart=gpt4, long=gpt3.5-16k
    @hide_output_parse: bool, hide the llm's output that output interpreters will parse, default True
    """
    memory = None
    interpreters = []
    model_type = 'normal'
    hide_output_parse = False

    def add_role_prompt(self, prompt):
        """
        add role prompt
        """
        if len(self.interpreters) > 0 and self.interpreters[0].__class__.__name__ == 'RoleInterpreter':
            role_interpreter = self.interpreters[0]
            if role_interpreter.system_prompt is not None:
                role_interpreter.system_prompt += '\n' + prompt
            else:
                role_interpreter.system_prompt_template += '\n' + prompt

    @abc.abstractmethod
    async def run(self, input=None, output_callback=default_output_callback, input_for_memory_node_id=-1):
        """
        input: str, user's new input, None means continue to run where it stopped
        input_for_memory_node_id: int, -1 means input is not from memory, None means input new, otherwise input is for memory node
        output_callback: async function, output_callback(content: str) -> None
        """
        pass

    def stop(self):
        """
        stop the agent
        """
        self.stop_event.set()


    def __init__(self, workspace='./'):
        """
        @workspace: str, workspace path
        """
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.workspace = workspace

    @classmethod
    def empty(cls, workspace='./'):
        """
        empty agent, only role interpreter and memory, work like a basic LLM chatbot
        @workspace: str, workspace path
        """
        pass

    @classmethod
    def default(cls, workspace='./', retrieve_type='embedding'):
        """
        default agent, with all interpreters
        @workspace: str, workspace path
        @retrieve_type: str, 'embedding' or 'link'
        """
        pass
    
    @classmethod
    def with_functions(cls, functions, role_prompt=None, workspace = './', model_type='smart'):
        """
        functions: list, [function1, function2, ...]
        @role_prompt: str, role prompt
        @workspace: str, workspace path
        @import_code: str, import code
        @libs: str, libs
        """
        pass