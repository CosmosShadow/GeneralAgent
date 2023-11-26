from ast import Tuple
import os

def compile_tsx(lib_name:str, code:str, target_dir:str):
    """
    Compile tsx code into a UI library.
    @lib_name: the name of the UI library
    @code: the tsx code
    @target_dir: the directory to save the UI library
    """
    # 目标目录不存在就创建
    if os.path.exists(target_dir):
        import shutil
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    from GeneralAgent.utils import get_tsx_builder_dir
    ts_builder_dir = get_tsx_builder_dir()

    code_path = os.path.join(ts_builder_dir, 'src/lib/index.tsx')
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code)
    # 写入lib名称
    webpack_template_path = os.path.join(ts_builder_dir, 'webpack.config.template.js')
    webpack_template = ''
    with open(webpack_template_path, 'r', encoding='utf-8') as f:
        webpack_template = f.read()
    webpack_template = webpack_template.replace('LibTemplate', lib_name)
    webpack_path = os.path.join(ts_builder_dir, 'webpack.config.js')
    with open(webpack_path, 'w', encoding='utf-8') as f:
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
You are a React and Typescript expert.

# Task
Create a React function component named LibTemplate in tsx language. 
The component should have the following functionality:
{{task}}

# Import
Use the following import syntax:
```
const React = (window as any).React;
const antd = (window as any).antd;
```
No other import methods are allowed.

# DEMO

```tsx
const React = (window as any).React;
const antd = (window as any).antd;

const [Form, Input, Button] = [antd.Form, antd.Input, antd.Button];

const LibTemplate = ({save_data}: {save_data: (data:any)=>void}) => {
  // use save_data to save the data
}

export default LibTemplate;
```

Please reponse the component code which finish the task without any explaination.
"""

    from jinja2 import Template
    prompt = Template(prompt_template).render(task=task)
    messages = [{'role': 'system', 'content': prompt}]
    response = skills.llm_inference(messages, model_type="normal", stream=True)
    result = ''
    for token in response:
        # print(token, end='', flush=True)
        result += token
    result = result.replace('LibTemplate', lib_name)
    return result


def extract_tsx_code(content):
    """
    Extract tsx code from markdown content.
    """
    import re
    # 兼容tsx和ts
    pattern = re.compile(r'```tsx?\n([\s\S]*)\n```')
    match = pattern.search(content)
    if match:
        return match.group(1)
    else:
        return content

# def create_ui(task: str, ui_dir: str = './ui', component_name: str = None) -> (str, str):
#     """
#     Convert task into UI components. Return (component_name, js_path) tuple.
#     """
def create_ui(task: str, ui_dir: str = './ui', component_name: str = None) -> (str, str):
    """
    Convert a given task description into UI components.

    Args:
        task: A string representing the task description with all the necessary details.

    Returns:
        A tuple containing the name of the UI component and the path to the JavaScript file.

    Example:
        create_ui('A task description with all the necessary details')
    """
    import uuid
    import os
    lib_name = component_name
    if lib_name is None:
        lib_name = 'Lib' + str(uuid.uuid1())[:4]
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir)
    target_dir = os.path.join(ui_dir, lib_name)
    for _ in range(2):
        content = _llm_write_ui_lib(lib_name, task)
        code = extract_tsx_code(content)
        success = compile_tsx(lib_name, code, target_dir)
        if success:
            return lib_name, os.path.join(target_dir, 'index.js')
    return None

def parse_tsx_to_ui(code, save_dir=None):
    import uuid
    lib_name = 'Lib' + str(uuid.uuid1())[:4]
    if save_dir is None:
        from GeneralAgent import skills
        save_dir = skills.get_code_dir()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    target_dir = os.path.join(save_dir, lib_name)
    success = compile_tsx(lib_name, code, target_dir)
    if success:
        return lib_name, os.path.join(target_dir, 'index.js')
    else:
        return None