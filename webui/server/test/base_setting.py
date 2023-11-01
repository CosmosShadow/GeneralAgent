# 添加上级目录
import os, sys
import requests
import pytest
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HPPT_HOST = 'http://127.0.0.1:7777'
WS_HOST = HPPT_HOST.replace('http', 'ws')

def clear_bot(bot_id):
    url = HPPT_HOST + '/clear/' + bot_id
    result = requests.post(url)

def get_chats(bot_id):
    url = HPPT_HOST + '/chats/' + bot_id
    result = requests.get(url)
    return result.json()

def get_messages(bot_id, chat_id):
    url = HPPT_HOST + '/messages/'
    data = {
        'bot_id': bot_id,
        'chat_id': chat_id
    }
    result = requests.post(url, json=data)
    return result.json()