# 知识库解析器
# 使用: https://github.com/run-llama/llama_index 库构建知识库索引
# 默认使用 GeneralAgent.skills 中 embedding_texts 函数来embedding，你可以重写 embedding_texts 函数

# def new_embedding_texts(texts) -> [[float]]:
#     """
#     对文本数组进行embedding
#     """
#     import os
#     client = _get_openai_client()
#     model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')
#     resp = client.embeddings.create(input=texts, model=model)
#     result = [x.embedding for x in resp.data]
#     return result
# from GeneralAgent import skills
# skills.embedding_texts = new_embedding_texts


from .interpreter import Interpreter

import os
import json
import shutil

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from typing import Any, List
from llama_index.core.embeddings import BaseEmbedding

from GeneralAgent import skills


class CustomEmbeddings(BaseEmbedding):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

    @classmethod
    def class_name(cls) -> str:
        return "CustomEmbeddings"

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    def _get_query_embedding(self, query: str) -> List[float]:
        return skills.embedding_texts([query])[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        return skills.embedding_texts([text])[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return skills.embedding_texts(texts)

from llama_index.core import Settings
embed_model = CustomEmbeddings(embed_batch_size=16)
Settings.embed_model = embed_model


class KnowledgeInterperter(Interpreter):
    """
    知识库解析器，用户解析知识库的问题
    """
    def __init__(self, workspace, knowledge_files=[], rag_function=None) -> None:
        """
        @param workspace: 工作目录
        @param knowledge_files: 知识库文件列表，可以是本地文件或者网络文件，比如['http://xxx.txt', './xxx.pdf']，支持格式为llama库支持的格式
        @param rag_function: 查询函数，输入问题，返回答案列表
        """
        self.workspace = workspace
        self.knowledge_files = knowledge_files
        self.rag_function = rag_function
        self.work = len(knowledge_files) > 0 or (rag_function is not None)

        if len(knowledge_files) > 0:
            self._create_index()
        else:
            self.index = None

    def _create_index(self):
        """
        构建索引
        """
        llama_dir = os.path.join(self.workspace, 'llama')
        meta_path = os.path.join(llama_dir, 'meta.json')
        data_dir = os.path.join(llama_dir, 'data')
        storage_dir = os.path.join(llama_dir, 'storage')

        if not os.path.exists(llama_dir):
            os.makedirs(llama_dir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        # 判断是否需要重新构建索引
        files_change = False
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            # 使用set比较两个列表是否相等
            if set(meta['knowledge_files']) != set(self.knowledge_files):
                files_change = True
        else:
            files_change = True

        # 如果文件有变化，重新构建索引
        if files_change:
            # 删除data目录下的所有文件 & 使用 shutil 库 拷贝knowledge_files到data目录下
            for file in os.listdir(data_dir):
                os.remove(os.path.join(data_dir, file))
            for file in self.knowledge_files:
                # 如果文件是网络文件，下载到data目录下
                if file.startswith('http'):
                    import requests
                    res = requests.get(file)
                    file_name = file.split('/')[-1]
                    with open(os.path.join(data_dir, file_name), 'wb') as f:
                        f.write(res.content)
                else:
                    file_name = os.path.basename(file)
                    shutil.copy(file, os.path.join(data_dir, file_name))
            # 重新构建索引
            documents = SimpleDirectoryReader(data_dir).load_data()
            self.index = VectorStoreIndex.from_documents(documents)
            self.index.storage_context.persist(persist_dir=storage_dir)
            with open(meta_path, 'w') as f:
                json.dump({'knowledge_files': self.knowledge_files}, f)
        else:
            storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            self.index = load_index_from_storage(storage_context)

    def prompt(self, messages) -> str:
        if len(messages) == 0:
            return ''
        if len(self.knowledge_files) == 0 and self.rag_function is None:
            return ''
        background = 'Background:'
        if len(self.knowledge_files) > 0:
            nodes = self.index.as_retriever().retrieve(messages[-1]['content'])
            for node in nodes:
                background += '\n' + node.get_text()
            background += '\n' + '\n'.join(self.knowledge_files)
        if self.rag_function is not None:
            background += '\n' + self.rag_function(messages)
        return background