import os
from GeneralAgent.memory import LinkMemory
from GeneralAgent.utils import default_get_input, default_output_recall
from GeneralAgent.llm import llm_inference

class LinkAgent:
    def __init__(self, workspace) -> None:
        self.workspace = workspace
        self.link_memory = LinkMemory(os.path.join(workspace, 'link_memory.json'))

    async def run(self, input, output_recall=default_output_recall, show_detail=True):
        memory_output = output_recall if show_detail else None
        new_input = self.link_memory.add_content(input, 'user', memory_output)
        if len(new_input) > 0:
            messages = [
                {'role': 'system', 'content': 'You are a helpful assistant'},
                {'role': 'user', 'content': new_input}
                ]
            response = llm_inference(messages=messages)
            for token in response:
                await output_recall(token)