# 知识库解析器
from .interpreter import Interpreter

class KnowledgeInterperter(Interpreter):
    """
    知识库解析器，用户解析知识库的问题
    """
    def __init__(self, query_function) -> None:
        """
        @param query_function: 查询函数，输入问题，返回答案列表
        """
        self.query_function = query_function

    def prompt(self, messages) -> str:
        if len(messages) == 0:
            return ''
        else:
            input = messages[-1]['content']
            results = self.query_function(input)
            while len(''.join(results)) > 14 * 1000:
                results.pop()
            return 'Backgroun: \n' + '\n'.join(results)