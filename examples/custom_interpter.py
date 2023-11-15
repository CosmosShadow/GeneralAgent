
import re
import asyncio
from GeneralAgent.agent import Agent
from GeneralAgent.interpreter import Interpreter, RoleInterpreter
from GeneralAgent.utils import confirm_to_run

python_prompt = """
# Run python
* format is : ```python\\nthe_code\\n```
* the code will be executed
* python version is 3.9
"""

class CustomPythonInterpreter(Interpreter):
    input_match_pattern = None
    output_match_start_pattern = '```python\n'
    output_match_pattern = '```python\n(.*?)\n```'

    def parse(self, string) -> (str, bool):
        pattern = re.compile(self.match_template, re.DOTALL)
        code = pattern.search(string).group(1)
        if confirm_to_run():
            exec(code)
        return '' , False

    def prompt(self, messages) -> str:
        return python_prompt

async def main():
    agent = Agent()
    agent.interpreters = [RoleInterpreter(), CustomPythonInterpreter()]
    while True:
        input_content = input('>>>')
        await agent.run(input_content)

if __name__ == '__main__':
    asyncio.run(main())