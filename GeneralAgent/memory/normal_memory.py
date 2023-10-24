# Memeory
import json
import os

class NormalMemory:
    def __init__(self, serialize_path='./memory.json'):
        self.messages = []
        if os.path.exists(serialize_path):
            with open(serialize_path, 'r') as f:
                self.messages = json.load(f)

    def add_message(self, role, content):
        self.messages.append({'role': role, 'content': content})
        with open('./memory.json', 'w') as f:
            json.dump(self.messages, f)

    def get_messages(self):
        return self.messages