# read the document and can retrieve the information
import re
from .interpreter import Interpreter
import chromadb
from GeneralAgent.llm import embedding_batch, num_tokens_from_string

def _split_text(text, max_len):
    """
    Splits a given text into segments of up to max_len characters, using punctuation marks as delimiters.
    """
    import re
    segments = []
    current_segment = ""
    for sentence in re.split(r"[，。,.;；]", text):
        # 本身就是大于max_len的句子
        if len(sentence) > max_len:
            for i in range(0, len(sentence), max_len):
                segments.append(sentence[i:i+max_len])
        else:
            if len(current_segment + sentence) <= max_len:
                current_segment += sentence
            else:
                segments.append(current_segment)
                current_segment = sentence
    if current_segment:
        segments.append(current_segment)
    return segments

def _merge_short_strings(paragraphs, min_length=100):
    merged_paragraphs = []
    current_string = ""
    for p in paragraphs:
        current_string += ' ' + p
        if len(current_string) < min_length:
            continue
        else:
            merged_paragraphs.append(current_string)
            current_string = ''
    if len(current_string) > 0:
        merged_paragraphs.append(current_string)
    return merged_paragraphs

# 文本转换为段落
def _text_to_paragraphs(text, max_len=510):
    if len(text) == 0:
        return []
    
    # 粗略分段
    paragraph_list = text.split("\n")

    # 合并短句
    paragraph_list = _merge_short_strings(paragraph_list)

    results = []

    # 再精细分段
    for paragraph in paragraph_list:
        if len(paragraph) == 0:
            continue
        if len(paragraph) * 2 <= max_len:
            results.append(paragraph)
        else:
            results += _split_text(paragraph, max_len)
    results = [x.strip() for x in results if len(x.strip()) > 0]
    return results



class ReadInterpreter(Interpreter):
    def __init__(self, serialize_path='./read_data/', prompt_max_length=1000, useful_msg_count=2) -> None:
        self.prompt_max_length = prompt_max_length
        self.useful_msg_count = useful_msg_count
        self.client = chromadb.PersistentClient(path=serialize_path)
        self.collection = self.client.get_or_create_collection(name="read", metadata={"hnsw:space": "cosine"})

    def prompt(self, messages) -> str:
        querys = []
        for x in messages[-self.useful_msg_count:]:
            querys += _text_to_paragraphs(x['content'])
        query_embeddings = embedding_batch(querys)
        result = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=2,
        )
        distances = [x for z in result['distances'] for x in z]
        documents = [x for z in result['documents'] for x in z]
        # sort and filter distance < 100
        documents = [x for _, x in filter(sorted(zip(distances, documents), key=lambda x: x[0]), lambda x: x[0] < 100)]
        # texts token count should less than prompt_max_length
        texts = []
        texts_token_count = 0
        for x in documents:
            if texts_token_count + num_tokens_from_string(x) > self.prompt_max_length:
                break
            texts.append(x)
        return '\n'.join(texts)

    @property
    def match_template(self):
        return '```read\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        file_paths = match.group(1).strip().split('\n')
        paragraphs = []
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                paragraphs += _text_to_paragraphs(text)
        embeddings = embedding_batch(paragraphs)
        self.collection.add(
            documents=paragraphs,
            embeddings=embeddings,
            metadatas=[{} for _ in paragraphs],
        )