# Memeory
import json
import os

class NormalMemory:
    def __init__(self, serialize_path='./memory.json'):
        self.messages = []
        self.serialize_path = serialize_path
        if os.path.exists(serialize_path):
            with open(serialize_path, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)

    def save(self):
        with open(self.serialize_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f)

    def add_message(self, role, content):
        assert role in ['user', 'assistant']
        self.messages.append({'role': role, 'content': content})
        self.save()

    def append_message(self, role, content):
        assert role in ['user', 'assistant']
        if len(self.messages) > 0 and self.messages[-1]['role'] == role:
            self.messages[-1]['content'] += '\n' + content
        else:
            self.messages.append({'role': role, 'content': content})
        self.save()

    def get_messages(self):
        return self.messages
    

def test_NormalMemory():
    serialize_path = './memory.json'
    mem = NormalMemory(serialize_path=serialize_path)
    mem.add_message('user', 'hello')
    mem.add_message('assistant', 'hi')
    mem = NormalMemory(serialize_path=serialize_path)
    assert len(mem.get_messages()) == 2
    mem.append_message('assistant', 'hi')
    assert len(mem.get_messages()) == 2