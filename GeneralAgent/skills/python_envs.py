
def get_current_env_python_libs() -> str:
    """
    Return the python libs that installed in current env
    """
    import os
    requirements_path = os.path.join(os.path.dirname(__file__), '../../requirements.txt')
    with open(requirements_path, 'r') as f:
        requirements = f.read()
        requirements = requirements.replace('\n', ' ')
        return requirements.strip()
    
def get_python_version() -> str:
    """
    Return the python version, like "3.9"
    """
    return '3.9'

def get_python_code(content:str) -> str:
    """
    Return the python code text from content
    """
    template = '```python\n(.*?)\n```'
    import re
    code = re.findall(template, content, re.S)
    if len(code) > 0:
        return code[0]
    else:
        return content