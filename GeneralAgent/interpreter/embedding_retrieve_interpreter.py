# read the document and can retrieve the information
import re
from .interpreter import Interpreter
import chromadb
import logging

class EmbeddingRetrieveInterperter(Interpreter):
    """
    EmbeddingRetrieveInterperter can retrieve the information from the memory by embedding.
    """
    
    input_match_pattern = '```read\n(.*?)\n```'

    def __init__(self, serialize_path='./read_data/', prompt_max_length=1000, useful_msg_count=2) -> None:
        self.prompt_max_length = prompt_max_length
        self.useful_msg_count = useful_msg_count
        self.client = chromadb.PersistentClient(path=serialize_path)
        self.collection = self.client.get_or_create_collection(name="read", metadata={"hnsw:space": "cosine"})

    def prompt(self, messages) -> str:
        from GeneralAgent import skills
        # when collection is empty, return empty string
        if self.collection.count() == 0:
            return ''
        
        querys = []
        for x in messages[-self.useful_msg_count:]:
            querys += skills.split_text(x['content'], 200)
        query_embeddings = skills.embedding_batch(querys)
        result = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=2,
        )
        # extract distances and documents
        distances = [x for z in result['distances'] for x in z]
        documents = [x for z in result['documents'] for x in z]

        # sort distances and documents by distance
        sorted_docs = sorted(list(zip(distances, documents)), key=lambda x: x[0])

        # filter documents with distance < 100
        documents = [x for d, x in sorted_docs if d < 100]
        # texts token count should less than prompt_max_length
        texts = []
        texts_token_count = 0
        for x in documents:
            if texts_token_count + skills.string_token_count(x) > self.prompt_max_length:
                break
            texts.append(x)
        return '\n'.join(texts)
    
    def input_parse(self, string) -> (str, bool):
        from GeneralAgent import skills
        information = []
        pattern = re.compile(self.input_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        file_paths = match.group(1).strip().split('\n')
        for file_path in file_paths:
            paragraphs = skills.split_text(skills.read_file_content(file_path), max_token=300)
            if len(paragraphs) > 0:
                information.append(f'The content of file {file_path} is: ' + '\n'.join(paragraphs)[:100] + '\n......')
            embeddings = skills.embedding_batch(paragraphs)
            # logging.debug(paragraphs[:2])
            # logging.debug(embeddings[:2])
            self.collection.add(
                documents=paragraphs,
                embeddings=embeddings,
                metadatas=[{'file_path': file_path} for _ in paragraphs],
                ids=[file_path+str(i) for i in range(len(paragraphs))],
            )
        stop = False
        if string.replace(match.group(0), '').strip() == '':
            stop = True
        info = '\n'.join(information)
        string = f'\n{string}\n```{info}```\n'
        return string, stop