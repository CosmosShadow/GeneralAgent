import abc
import os, re
import asyncio
import logging
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.memory import Memory, MemoryNode
from GeneralAgent.interpreter import PlanInterpreter, EmbeddingRetrieveInterperter, LinkRetrieveInterperter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, ShellInterpreter, AppleScriptInterpreter, FileInterpreter


class AbsAgent(metaclass=abc.ABCMeta):
    """
    workspace: str, workspace path
    memory: Memory, memory
    input_interpreters: list, input interpreters
    output_interpreters: list, output interpreters
    retrieve_interpreters: list, retrieve interpreters
    model_type: str, 'normal' or 'smart' or 'long'. For OpenAI api, normal=gpt3.5, smart=gpt4, long=gpt3.5-16k
    hide_output_parse: bool, hide the llm's output that output interpreters will parse, default True
    """
    memory = None
    input_interpreters = []
    retrieve_interpreters = []
    output_interpreters = []
    model_type = 'normal',
    hide_output_parse = True

    @abc.abstractmethod
    async def run(self, input=None, output_callback=default_output_callback, input_for_memory_node_id=-1):
        """
        input: str, user's new input, None means continue to run where it stopped
        input_for_memory_node_id: int, -1 means input is not from memory, None means input new, otherwise input is for memory node
        output_callback: async function, output_callback(content: str) -> None
        """
        pass

    def stop(self):
        self.stop_event.set()

    def __init__(self, workspace='./'):
        """
        workspace: str, workspace path
        memory: Memory, memory
        input_interpreters: list, input interpreters
        output_interpreters: list, output interpreters
        retrieve_interpreters: list, retrieve interpreters
        model_type: str, 'normal' or 'smart' or 'long'. For OpenAI api, normal=gpt3.5, smart=gpt4, long=gpt3.5-16k
        hide_output_parse: bool, hide the llm's output that output interpreters will parse, default True
        """
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.workspace = workspace

    @classmethod
    def default(cls, workspace):
        pass
    
    @classmethod
    def empty(cls, workspace):
        pass

    @classmethod
    def with_functions(cls, functions, role_prompt=None, workspace = './', model_type='smart'):
        pass
    
    @classmethod
    def with_link_memory(cls, workspace):
        pass