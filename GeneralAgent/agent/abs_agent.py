import abc
import os


class AbsAgent(metaclass=abc.ABCMeta):
    """
    Abstract Agent
    @memory: Memory
    @interpreters: list, interpreters
    @model_type: str, 'normal' or 'smart' or 'long'. For OpenAI api, normal=gpt3.5, smart=gpt4, long=gpt3.5-16k
    @output_callback: function, output_callback(content: str) -> None
    @python_run_result: str, python run result
    @run_level: int, python run level, use for check stack overflow level
    """
    memory = None
    interpreters = []
    model_type = 'smart'
    output_callback = None
    python_run_result = None
    run_level = 0
    chat_messages_limit = None # chat messages limit, default None means no limit
    continue_run = True
    disable_python_run = False

    @abc.abstractmethod
    def run(self, input, return_type=str):
        """
        agent run: parse intput -> get llm messages -> run LLM and parse output
        @input: str, user's new input, None means continue to run where it stopped
        @return_type: type, return type, default str
        """

    def __init__(self, workspace=None):
        """
        @workspace: str, workspace path
        """
        if workspace is not None and not os.path.exists(workspace):
            os.makedirs(workspace)
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

    def delete():
        """
        删除Agent: 删除记忆、python序列化结果等
        """
        pass