# 知识库解析器
from .interpreter import Interpreter

class KnowledgeInterperter(Interpreter):
    """
    知识库解析器，用户解析知识库的问题
    """
    def __init__(self, knowledge_files=[], rag_function=None) -> None:
        """
        @param rag_function: 查询函数，输入问题，返回答案列表
        """
        self.work = len(knowledge_files) > 0 or (rag_function is not None)
        self.knowledge_files = knowledge_files
        self.rag_function = rag_function

    def prompt(self, messages) -> str:
        if not self.work:
            return ''
        if len(messages) == 0:
            return ''
        else:
            results = self.rag_function(messages)
            return 'Background: \n' + '\n'.join(results)