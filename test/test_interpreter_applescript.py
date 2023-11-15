from GeneralAgent.interpreter import AppleScriptInterpreter

def test_match():
    content = """```\napplescript\nxxxx\n```"""
    interpreter = AppleScriptInterpreter()
    assert interpreter.output_match(content)

def test_open_url():
    import platform
    system = platform.system()
    if system != 'Darwin':
        return
    interpreter = AppleScriptInterpreter()
    content = """```applescript
tell application "Safari"
    activate
    open location "https://www.google.com"
end tell
```"""
    output, is_stop = interpreter.output_parse(content)
    assert is_stop is False
    assert output.strip() == 'run successfully'


if __name__ == '__main__':
    test_match()
    test_open_url()
