from base_setting import *
from GeneralAgent.interpreter import AppleScriptInterpreter

def test_match():
    content = """```\napplescript\nxxxx\n```"""
    interpreter = AppleScriptInterpreter()
    assert interpreter.match(content)

def test_open_url():
    interpreter = AppleScriptInterpreter()
    content = """```applescript
tell application "Safari"
    activate
    open location "https://www.google.com"
end tell
```"""
    output, is_stop = interpreter.parse(content)
    assert is_stop is False
    assert output.strip() == 'run successfully'


if __name__ == '__main__':
    test_match()
    test_open_url()
