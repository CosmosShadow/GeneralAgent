# Disable Python Run
# 默认情况下，GeneralAgent会运行用户输入的Python代码。如果你不希望GeneralAgent运行Python代码，可以通过将 `disable_python_run` 属性设置为 `True` 来禁用Python运行。
from GeneralAgent.agent import Agent

agent = Agent('你是一个python专家，辅助用户解决python问题。')
agent.disable_python_run = True
agent.user_input('用python实现一个读取文件的函数')

# 当然，这里是一个用Python实现的读取文件内容的函数：

# ```python
# def read_file(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             content = file.read()
#         return content
#     except FileNotFoundError:
#         return "File not found."
#     except Exception as e:
#         return f"An error occurred: {e}"

# # 示例用法
# file_content = read_file('example.txt')
# file_content
# ```

# 这个函数 `read_file` 接受一个文件路径作为参数，尝试以UTF-8编码读取文件内容，并返回读取到的内容。如果文件未找到或发生其他错误，则返回相应的错误信息。