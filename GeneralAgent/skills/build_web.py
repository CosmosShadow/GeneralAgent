import os

def _build_ui(lib_name, code, target_dir):
    # 目标目录不存在就创建
    if os.path.exists(target_dir):
        import shutil
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    ts_builder_dir = os.path.join(os.path.dirname(__file__), '../../webui/server/server/ts_builder')

    code_path = os.path.join(ts_builder_dir, 'src/lib/index.tsx')
    with open(code_path, 'w') as f:
        f.write(code)
    # 写入lib名称
    webpack_template_path = os.path.join(ts_builder_dir, 'webpack.config.template.js')
    webpack_template = ''
    with open(webpack_template_path, 'r') as f:
        webpack_template = f.read()
    webpack_template = webpack_template.replace('LibTemplate', lib_name)
    webpack_path = os.path.join(ts_builder_dir, 'webpack.config.js')
    with open(webpack_path, 'w') as f:
        f.write(webpack_template)
    # 获取编译的标准输出
    output = os.popen(f"cd {ts_builder_dir} && npm run build").read()
    if 'successfully' not in output:
        print(output)
        return False
    # 将编译后的文件移动到目标目录
    os.system(f"mv {ts_builder_dir}/build/* {target_dir}")
    return True


def _llm_write_ui_lib(lib_name, task):
    from GeneralAgent import skills
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

interface Props {
  data: any;
  send_data: (data: any) => void;
}

const LibTemplate = (props:Props) => {
    // props.data: the data from the backend.
    // props.send_data: a function that can send data (a dictionary) to the backend.
}
export default LibTemplate;
```

# Component functionality

{{task}}

Help me implement this LibTemplate component.
Only response the code without any explain.
"""
    from jinja2 import Template
    prompt = Template(prompt_template).render(task=task)
    messages = [
        {'role': 'system', 'content': 'You are a web frontend expert.'},
        {'role': 'user', 'content': prompt}
        ]
    response = skills.llm_inference(messages)
    result = ''
    for token in response:
        # print(token, end='', flush=True)
        result += token
    result = result.replace('LibTemplate', lib_name)
    return result


def _extract_tsx_code(content):
    import re
    # 兼容tsx和ts
    pattern = re.compile(r'```tsx?\n([\s\S]*)\n```')
    match = pattern.search(content)
    if match:
        return match.group(1)
    else:
        return content
    
def task_to_ui_js(task:str, ui_dir:str='./ui', lib_name:str=None) -> (str, str):
    """
    Convert task into UI components. task: task description, ui_dir: js component storage directory, lib_name: UI component name. And return the js file path and lib name. normally, you can ignore ui_dir and lib_name.
    """
    import uuid
    if lib_name is None:
        lib_name = 'Lib' + str(uuid.uuid1())[:4]
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir)
    target_dir = os.path.join(ui_dir, lib_name)
    content = _llm_write_ui_lib(lib_name, task)
    code = _extract_tsx_code(content)
    success = _build_ui(lib_name, code, target_dir)
    if success:
        return os.path.join(target_dir, 'index.js'), lib_name
    else:
        return None