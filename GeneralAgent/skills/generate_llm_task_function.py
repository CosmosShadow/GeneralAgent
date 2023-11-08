def generate_llm_task_function(task_description):
    """
    This function generates a Python function to perform a specific task using a large language model (LLM).
    
    Parameters:
    task_description (str): A description of the task that the generated function should perform.

    Returns:
    str: The generated Python function code as a string.
    """
    from GeneralAgent import skills
    from jinja2 import Template
    prompt_template = """
You are a Python expert.
Your job is to have a large language model (LLM) perform specific tasks, such as translation, planning, answering general knowledge questions, etc.
Large language model calling function:

```python
def simple_llm_inference(messages, json_schema):
     \"\"\"
     Run LLM (large language model) inference on the provided messages
    
     Parameters:
     messages: Input messages for the model, like [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'What is your name ?'}]
     json_schema: the json schema of return dictionary, like {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer" }}}

     Returns:
     returned as a dictionary According to the provided JSON schema.

     Note:
     The total number of tokens in the messages and the returned string must be less than 8000.
     \"\"\"
```

# Installed libraries:

[numpy]

# Your output's structure like below

```python
def xxx(xxx):
     \"\"\"
     xxx
     \"\"\"
     from GeneralAgent import skills
     # skills.simple_llm_inference
```

# Task

{{task}}

# Note:

- All imports should be placed inside the function.
- While creating your function, consider the all edge cases.
- Do not use any other libraries except simple_llm_inference and installed libraries.
- The simple_llm_inference function requires that the input messages are less than 8000, and the output length is less than 8000. - 
- When the task cannot be completed through one simple_llm_inference, you should consider task disassembly.
"""
    prompt = Template(prompt_template).render({'task': task_description})
    result = skills.llm_inference([{'role': 'system', 'content': prompt}, {'role': 'user', 'content': 'You are a python expert.'}, {'role': 'user', 'content': prompt}], model_type="smart")
    code = skills.get_python_code(result)
    return code
    