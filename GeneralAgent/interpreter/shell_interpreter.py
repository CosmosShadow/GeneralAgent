import re
from .interpreter import Interpreter
from GeneralAgent.utils import confirm_to_run

shell_prompt = """
# Run shell
* format is : ```shell\\nthe_command\\n```
* the command will be executed
"""

class ShellInterpreter(Interpreter):

    match_start_pattern = '```shell\n'
    match_pattern = '```shell\n(.*?)\n```'
    
    def __init__(self, workspace='./') -> None:
        self.workspace = workspace

    async def prompt(self, messages) -> str:
        return shell_prompt

    async def parse(self, string):
        pattern = re.compile(self.match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        if confirm_to_run():
            output = self._run_bash(match.group(1))
            return output.strip(), False
        else:
            return '', False

    def _run_bash(self, content):
        sys_out = ''
        import subprocess
        if 'python ' in content:
            content = content.replace('python ', 'python3 ')
        try:
            p = subprocess.Popen(content, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            pass
        finally:
            sys_out, err = p.communicate()
            sys_out = sys_out.decode('utf-8')
        return sys_out