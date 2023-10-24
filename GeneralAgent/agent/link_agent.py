import os
from GeneralAgent.memory import LinkMemory

class LinkAgent:
    def __init__(self, workspace) -> None:
        self.workspace = workspace
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.link_memory = LinkMemory(os.path.join(workspace, 'link_memory.json'))

    async def read_content(self, content):
        await self.link_memory.add_memory(content)

    async def run(self, messages, output_callback):
        from skills import skills
        recall_memory = await self.link_memory.get_memory(messages)
        model_messages = [
            {'role': 'system', 'content': 'You are a helpful assistant'},
            {'role': 'system', 'content': f'Background:\n{recall_memory}'},
            ]
        cut_messages = skills.cut_messages(messages, 2000)
        model_messages += cut_messages
        # print(model_messages)
        response = skills.llm_inference(model_messages)
        for token in response:
            await output_callback(token)