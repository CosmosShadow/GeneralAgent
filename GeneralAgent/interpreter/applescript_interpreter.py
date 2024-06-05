import re
from .interpreter import Interpreter

applescript_promt = """
# Run applescript
* Here are the commands
```applescript
<applescript_command>
```
* the command will be executed if in macOS computer.
"""

class AppleScriptInterpreter(Interpreter):
    output_match_pattern = '```(\n)?applescript(.*?)\n```'

    def prompt(self, messages) -> str:
        return applescript_promt
    
    def output_parse(self, string) -> (str, bool):
        pattern = re.compile(self.output_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        sys_out = self._run_applescript(match.group(2))
        return sys_out.strip(), True

    def _run_applescript(self, content):
        content = content.replace('"', '\\"')
        sys_out = ''
        import subprocess
        try:
            p = subprocess.Popen('osascript -e "{}"'.format(content), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            pass
        finally:
            sys_out, err = p.communicate()
            sys_out = sys_out.decode('utf-8')
        sys_out = sys_out.strip()
        if sys_out == '':
            sys_out = 'run successfully'
        return sys_out