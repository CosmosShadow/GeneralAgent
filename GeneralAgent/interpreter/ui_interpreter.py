import re
from .interpreter import Interpreter
from GeneralAgent.utils import confirm_to_run


class UIInterpreter(Interpreter):
    send_ui = None
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

    def __init__(self, workspace='./', send_ui=None) -> None:
        """
        :param workspace: workspace for the interpreter
        :param send_ui: the async function to send ui to user
        """
        self.workspace = workspace
        self.send_ui = send_ui

    async def prompt(self, messages) -> str:
        return self.ui_prompt

    @property
    def match_template(self):
        return '```tsx\n(.*?)\n```'

    async def parse(self, string):
        from GeneralAgent import skills
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        code = match.group(1)
        lib_name, js_path = skills.parse_tsx_to_ui(code)
        if self.send_ui is not None:
            await self.send_ui(js_path)
        return string, True