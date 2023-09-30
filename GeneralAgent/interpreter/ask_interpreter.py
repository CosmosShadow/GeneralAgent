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
    def prompt(self, messages) -> str:
        return ask_prompt
    
    @property
    def match_template(self):
        return '```ask\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        question = match.group(1).strip()
        return '', True