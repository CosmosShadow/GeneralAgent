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

    def push_stack(self):
        pass

    def pop_stack(self):
        pass

    def add_message(self, role, content):
        """
        add a new message
        @role: str, 'user' or 'assistant'
        @content: str, message content
        return message id
        """
        assert role in ['user', 'assistant']
        self.messages.append({'role': role, 'content': content})
        self.save()
        return len(self.messages) - 1

    def append_message(self, role, content, message_id=None):
        """
        append a message. when message_id is not None, append to the message with message_id and move it to the end
        @role: str, 'user' or 'assistant'
        @content: str, message content
        return message id
        """
        self.simple_print()
        assert role in ['user', 'assistant']
        if message_id is not None:
            assert message_id >= 0 and message_id < len(self.messages)
            assert self.messages[message_id]['role'] == role
            self.messages[message_id]['content'] += '\n' + content
            # self.messages.append(self.messages.pop(message_id))
            self.messages = self.messages[:message_id+1]
            self.save()
            self.simple_print()
            return len(self.messages) - 1
        else:
            if len(self.messages) > 0 and self.messages[-1]['role'] == role:
                self.messages[-1]['content'] += '\n' + content
            else:
                self.messages.append({'role': role, 'content': content})
            self.save()
            self.simple_print()
            return len(self.messages) - 1

    def get_messages(self):
        return self.messages
    
    def __str__(self):
        return json.dumps(self.messages, indent=4)
    
    def simple_print(self):
        print('-' * 50 + '<Memory>' + '-' * 50)
        for message in self.messages:
            print('[[' + message['role'] + ']]: ' + message['content'][:100])
        print('-' * 50 + '</Memory>' + '-' * 50)

def test_NormalMemory():
    serialize_path = './memory.json'
    mem = NormalMemory(serialize_path=serialize_path)
    mem.add_message('user', 'hello')
    mem.add_message('assistant', 'hi')
    mem = NormalMemory(serialize_path=serialize_path)
    assert len(mem.get_messages()) == 2
    mem.append_message('assistant', 'hi')
    assert len(mem.get_messages()) == 2