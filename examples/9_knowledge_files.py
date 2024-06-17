# 知识库
from GeneralAgent import Agent

files = ['../docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf']
workspace = '9_knowledge_files'
agent = Agent('你是AI助手，用中文回复。', workspace=workspace, knowledge_files=files)
agent.user_input(['Self call 是什么意思？'])

# 清理掉
import shutil
shutil.rmtree(workspace)


# 知识库默认使用 GeneralAgent.skills 中 embedding_texts 函数来对文本进行 embedding (默认是OpenAI的text-embedding-3-small模型)
# 你可以重写 embedding_texts 函数，使用其他厂商 或者 本地的 embedding 方法，具体如下:

# def new_embedding_texts(texts) -> [[float]]:
#     """
#     对文本数组进行embedding
#     """
#     # 你的embedding方法
#     return result
# from GeneralAgent import skills
# skills.embedding_texts = new_embedding_texts