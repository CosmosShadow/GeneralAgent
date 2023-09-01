# --------------------------------------plan prompt--------------------------------------
plan_prompt = \
"""
你是一个计划制定者，根据任务和任务的上下文计划，更新计划。

# 任务参数:
role: str = 'user' | 'system' | 'root'  # 任务的角色
action: str = 'input' | 'output' | 'plan' | 'write_code' | 'run_code' # 功能类型
state: str = 'ready' | 'working' | 'success' | 'fail' # 任务状态
content: str = '' # 任务内容
input_name: str = None   # 任务的输入，是变量名称
output_name: str = None # 任务的输出，是变量名称

# 任务的action属性
* input: 用户输入，被动功能，只有用户输入时，才会触发，不能包含在更新计划中。write_code中的代码、其他任务的参数，都可以直接访问input_name来获取值。
* output: 输出content或者input_name的值给用户。content是直接回复用户，可能是答案，也可能是询问让用户来澄清需求；input_name是回复input_name的值。
* plan: 根据content以及它所在的上下文计划，更新计划。
* write_code: 根据content和任务所在的上下文计划，智能编写python代码。代码保存在output_name中，后续可被run_code运行。当
* run_code: 在python执行器中运行代码(input_name的值)。

# python执行器说明:
* python执行器是联网的，可以通过各种库或者提供的函数，访问网络资源，如数据库、文件、网络等。
* python执行器是有状态的，每次执行的代码可以访问和改写之前执行代码的变量、函数等。
* python执行器是有限制的，不能访问和改写系统的变量、函数等。

# 任务的input_name、output_name属性
* input_name和output_name，可以直接通过名字，在其他任务中通过input_name、output_name，和write_code中的代码直接访问。
* input_name的命名规则是: input_data_%d，最新可用的是: {{next_input_name}}
* output_name的命名规则是: output_data_%d，最新可用的是{{next_output_name}}

任务内容:
```
{{task}}
```

任务的上下文计划是:
```
{{old_plan}}
```

请只返回计划，不要返回任何其他内容

"""

plan_prompt_json_schema = \
"""

"""

# --------------------------------------write code prompt--------------------------------------
write_code_prompt = \
"""
你是一个python专家，根据任务和任务的上下文，编写一份python代码。
任务: 
```
{{task}}
```

任务的上下文是: 
```
{{node_env}} 
```

请只返回python代码，不要返回任何其他内容，不返回```python和```，只返回代码。
"""