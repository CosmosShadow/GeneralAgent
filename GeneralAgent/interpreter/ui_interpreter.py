import re
from .interpreter import Interpreter
from GeneralAgent.utils import confirm_to_run



class UIInterpreter(Interpreter):
    ui_prompt = """
# Return UI

"""

    def __init__(self, workspace='./') -> None:
        self.workspace = workspace

    async def prompt(self, messages) -> str:
        return self.shell_prompt

    @property
    def match_template(self):
        return '```tsx\n(.*?)\n```'

    async def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        code = match.group(1)
        output = self.run_code(code)
        return output.strip(), True

    def run_code(self, code):
        from GeneralAgent import skills
        lib_name, js_path = skills.parse_tsx_to_ui(code)
        # TODO: return ui to user
        # lib_name, os.path.join(target_dir, 'index.js')