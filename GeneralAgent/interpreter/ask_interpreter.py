# Interpreter
import re
from .interpreter import Interpreter

ask_prompt = """
# Ask question
* format is : ```ask\\nthe_question\\n```
* the question will be asked
* the answer will be saved in the memory
"""

class AskInterpreter(Interpreter):
    match_start_pattern = '```ask\n'
    match_pattern = '```ask\n(.*?)\n```'

    async def prompt(self, messages) -> str:
        return ask_prompt
    
    async def parse(self, string):
        pattern = re.compile(self.match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        question = match.group(1).strip()
        return '', True