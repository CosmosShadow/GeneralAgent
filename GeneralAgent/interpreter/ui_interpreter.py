import re
from .interpreter import Interpreter
import asyncio

class UIInterpreter(Interpreter):
    
    match_pattern = '```tsx\n(.*?)\n```'
    match_start_pattern = '```tsx\n'

    ui_prompt = """
# Send UI to user
Use the following tsx architecture to write a React component. The component will be compiled into a UI and sent to the user. The user's input can be sent to you through the save_data function.
```tsx
const React = (window as any).React;
const antd = (window as any).antd;

const [Form, Input, Button] = [antd.Form, antd.Input, antd.Button];

const LibTemplate = ({save_data}: {save_data: (data:any)=>void}) => {
  // use save_data to save the data
}

export default LibTemplate;
```
"""

    def __init__(self, send_ui, workspace=None) -> None:
        """
        :param send_ui: the async function to send ui to user
        :param workspace: workspace for the interpreter
        """
        self.send_ui = send_ui
        self.workspace = workspace

    async def prompt(self, messages) -> str:
        return self.ui_prompt

    async def parse(self, string):
        from GeneralAgent import skills
        pattern = re.compile(self.match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        code = match.group(1)
        lib_name, js_path = skills.parse_tsx_to_ui(code, save_dir=self.workspace)
        if self.send_ui is not None:
            async def delay_send_ui(lib_name, js_path):
                await asyncio.sleep(0.5)
                await self.send_ui(lib_name, js_path)
            asyncio.create_task(delay_send_ui(lib_name, js_path))
            print('Send UI to user successfuly.')
        return 'Send UI successfully', True