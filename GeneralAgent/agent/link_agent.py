import os
from GeneralAgent.memory import LinkMemory, NormalMemory
from GeneralAgent.utils import default_output_callback


class LinkAgent:
    def __init__(self, workspace='./'):
        self.workspace = workspace
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.normal_memory = NormalMemory(os.path.join(workspace, 'normal_memory.json'))
        self.link_memory = LinkMemory(os.path.join(workspace, 'link_memory.json'))

    async def read_content(self, content):
        await self.link_memory.add_memory(content)

    async def run(self, input, output_callback=default_output_callback):
        from GeneralAgent import skills
        # save and get messages
        self.normal_memory.add_message('user', input)
        messages = self.normal_memory.get_messages()
        # get recall memory
        recall_memory = await self.link_memory.get_memory(messages)
        model_messages = [
            {'role': 'system', 'content': 'You are a helpful assistant'},
            {'role': 'system', 'content': f'Background:\n{recall_memory}'},
            ]
        cut_messages = skills.cut_messages(messages, 2000)
        model_messages += cut_messages
        # print(model_messages)
        response = skills.llm_inference(model_messages, stream=True)
        for token in response:
            await output_callback(token)