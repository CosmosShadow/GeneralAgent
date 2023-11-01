import os
import json
import importlib.util
import logging
from jinja2 import Template

def load_applications():
    result = []
    current_dir = os.path.abspath(os.path.dirname(__file__))
    APPLICATIONS_PATH = os.path.join(current_dir, 'applications')
    for bot_name in os.listdir(APPLICATIONS_PATH):
        bot_dir = os.path.join(APPLICATIONS_PATH, bot_name)
        if os.path.isdir(bot_dir):
            bot_json_path = os.path.join(bot_dir, 'bot.json')
            if os.path.exists(bot_json_path):
                with open(bot_json_path, 'r') as f:
                    bot_json = json.load(f)
                    if 'icon' in bot_json:
                        bot_json['icon_url'] = os.path.join(APPLICATIONS_PATH, bot_name, bot_json['icon'])
                    bot_json['nickname'] = bot_json['name']
                    result.append(bot_json)
    return result


def load_application(bot_id):
    application = None
    current_dir = os.path.abspath(os.path.dirname(__file__))
    code_path = os.path.join(current_dir, f"./applications/{bot_id}/main.py")
    try:
        spec = importlib.util.spec_from_file_location("main", code_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        application = module
    except Exception as e:
        logging.exception(e)
    return application


def build_ui(lib_name, code, target_dir):
    # 目标目录不存在就创建
    if os.path.exists(target_dir):
        import shutil
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    code_path = os.path.join(os.path.dirname(__file__), './ts_builder/src/lib/index.tsx')
    with open(code_path, 'w') as f:
        f.write(code)
    # 写入lib名称
    webpack_template_path = os.path.join(os.path.dirname(__file__), './ts_builder/webpack.config.template.js')
    webpack_template = ''
    with open(webpack_template_path, 'r') as f:
        webpack_template = f.read()
    webpack_template = webpack_template.replace('LibTemplate', lib_name)
    webpack_path = os.path.join(os.path.dirname(__file__), './ts_builder/webpack.config.js')
    with open(webpack_path, 'w') as f:
        f.write(webpack_template)
    # 获取编译的标准输出
    output = os.popen(f"cd {os.path.dirname(__file__)}/ts_builder && npm run build").read()
    if 'successfully' not in output:
        print(output)
        return False
    # 将编译后的文件移动到目标目录
    os.system(f"mv {os.path.dirname(__file__)}/ts_builder/build/* {target_dir}")
    return True


def llm_write_ui_lib(lib_name, task):
    from skills import skills
    prompt_template = """
Help me write a React function component in tsx language.
Add some style to make the component display correctly and beautifully.
The component should be named LibTemplate.
The component should only use React and antd libraries, and the import should be done using the following syntax:
```
const React = (window as any).React;
const antd = (window as any).antd;
```
No other import methods are allowed.

# Your output should be like this:
```tsx
const React = (window as any).React;
const antd = (window as any).antd;

const [Form, Input, Button] = [antd.Form, antd.Input, antd.Button];

const LibTemplate = (data: any) => {
}
export default LibTemplate;
```

# Component functionality

{{task}}

Help me implement this LibTemplate component.
Only response the code without any explain.
"""
    prompt = Template(prompt_template).render(task=task)
    messages = [
        {'role': 'system', 'content': 'You are a web frontend expert.'},
        {'role': 'user', 'content': prompt}
        ]
    response = skills.llm_inference(messages)
    result = ''
    for token in response:
        print(token, end='', flush=True)
        result += token
    result = result.replace('LibTemplate', lib_name)
    return result


def extract_tsx_code(content):
    import re
    # 兼容tsx和ts
    pattern = re.compile(r'```tsx?\n([\s\S]*)\n```')
    match = pattern.search(content)
    if match:
        return match.group(1)
    else:
        return content
    
def task_to_ui_js(task, ui_dir='./ui', lib_name=None):
    import uuid
    if lib_name is None:
        lib_name = 'Lib' + str(uuid.uuid1())[:4]
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir)
    target_dir = os.path.join(ui_dir, lib_name)
    content = llm_write_ui_lib(lib_name, task)
    code = extract_tsx_code(content)
    success = build_ui(lib_name, code, target_dir)
    if success:
        return os.path.join(target_dir, 'index.js'), lib_name
    else:
        return None