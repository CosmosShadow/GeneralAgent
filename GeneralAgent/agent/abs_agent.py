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

    @classmethod
    def agent_builder(cls):
        """
        return a agent builder
        """
        role_prompt = """
You are an online Agent building robot.
You build and install the Agent by writing Python code to call predefined functions.
You mainly care about the core business process (function implementation), and do not need to care about input and output processing.

# For Example
```python
search_functions('scrape web page')
```

# Note:
- Don't make up functions that don't exist
- If the required function does not exist, you can build it through edit_function and generate_llm_task_function
- You can also uninstall the application according to user needs
- edit_application_code will handle user input and output, including text and files, you don't need to care.

# General process for building applications:
* Fully communicate needs with users
* search available functions(optional)
* edit normal function (optional)
* edit llm function (optional)
* edit application code (must)
* create application icon (must)
* update application meta (must)
* install application (must)
* uninstall_application (optional)
"""
        from GeneralAgent import skills
        functoins = [
            skills.search_functions,
            skills.edit_normal_function,
            skills.edit_llm_function,
            skills.edit_application_code,
            skills.create_application_icon,
            skills.update_application_meta,
            skills.install_application,
            skills.uninstall_application
        ]
        agent = cls.with_functions(functoins, role_prompt)
        return agent