import re
from .interpreter import Interpreter
import asyncio

class UIInterpreter(Interpreter):
    
    output_match_start_pattern = '```tsx\n'
    output_match_pattern = '```tsx\n(.*?)\n```'

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

    def __init__(self, send_ui, output_callback, workspace=None) -> None:
        """
        :param send_ui: the function to send ui to user
        :param workspace: workspace for the interpreter
        """
        self.send_ui = send_ui
        self.output_callback = output_callback
        self.workspace = workspace

    def prompt(self, messages) -> str:
        return self.ui_prompt

    def output_parse(self, string) -> (str, bool):
        from GeneralAgent import skills
        pattern = re.compile(self.output_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        code = match.group(1)
        lib_name, js_path = skills.parse_tsx_to_ui(code, save_dir=self.workspace)
        # Terminate the output callback
        self.output_callback(None)
        # Send UI to user
        self.send_ui(lib_name, js_path)
        print('Send UI to user successfuly.')
        return '', True