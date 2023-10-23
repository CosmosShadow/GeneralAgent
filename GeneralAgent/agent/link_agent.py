import os
from GeneralAgent.memory import LinkMemory
from GeneralAgent.utils import default_get_input, default_output_callback
from GeneralAgent.llm import llm_inference

class LinkAgent:
    def __init__(self, workspace) -> None:
        self.workspace = workspace
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.link_memory = LinkMemory(os.path.join(workspace, 'link_memory.json'))

    async def read_content(self, content):
        await self.link_memory.add_memory(content)

    async def run(self, messages, output_callback=default_output_callback):
        from skills import skills
        recall_memory = self.link_memory.get_memory(messages)
        model_messages = [
            {'role': 'system', 'content': 'You are a helpful assistant'},
            {'role': 'system', 'content': f'Background:\n{recall_memory}'},
            ]
        cut_messages = skills.cut_messages(messages, 2000)
        model_messages += cut_messages
        model = 'gpt-3.5-turbo'
        if skills.num_tokens_from_string(model_messages) > 3000:
            model = 'gpt-3.5-turbo-16k'
        response = llm_inference(model_messages, model)
        for token in response:
            await output_callback(token)