# read the document and can retrieve the information
import re
from .interpreter import Interpreter
import chromadb
    

class ReadInterpreter(Interpreter):
    def __init__(self, serialize_path='./read_data/') -> None:
        self.client = chromadb.PersistentClient(path=serialize_path)
        self.collection = self.client.get_or_create_collection(name="read")

    def prompt(self, messages) -> str:
        pass

    @property
    def match_template(self):
        return '```read\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        file_paths = match.group(1).strip().split('\n')
        for file_path in file_paths:
            pass