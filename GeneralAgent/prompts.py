write_code_prompt = """
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

