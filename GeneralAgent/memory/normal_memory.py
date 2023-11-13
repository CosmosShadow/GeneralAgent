# Memeory
import json
import os

class NormalMemory:
    def __init__(self, serialize_path='./memory.json'):
        self.messages = []
        if os.path.exists(serialize_path):
            with open(serialize_path, 'r') as f:
                self.messages = json.load(f)

    def save(self):
        with open('./memory.json', 'w') as f:
            json.dump(self.messages, f)

    def add_message(self, role, content):
        assert role in ['user', 'assistant']
        self.messages.append({'role': role, 'content': content})
        self.save()

    def append_message(self, role, content):
        assert role in ['user', 'assistant']
        if len(self.messages) > 0 and self.messages[-1]['role'] == role:
            self.messages[-1]['content'] += content
        else:
            self.messages.append({'role': role, 'content': content})
        self.save()

    def get_messages(self):
        return self.messages