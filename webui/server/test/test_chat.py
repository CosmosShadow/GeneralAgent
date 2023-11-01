from base_setting import *
import websockets
import logging
from server.interface import Message, Token
import json


@pytest.mark.asyncio
async def test_user_chat():
    bot_id = 'hello'
    clear_bot(bot_id)
    ws_url = WS_HOST + "/ws/user/"
    async with websockets.connect(ws_url) as ws:
        # 发送消息
        msg = '1 + 1 = ?'
        message = Message(bot_id=bot_id, msg=msg)
        await ws.send(message.to_text())
        logging.debug('send message success')
        # 接收消息，
        # 第一条: 发送成功的消息
        res = await ws.recv()
        message: Message = Message(**json.loads(res)['data'])
        logging.debug(message)
        logging.debug(message)
        assert msg.strip() == message.msg.strip()
        assert message.chat_id != ''
        # 回复消息: token + message
        result = ''
        msg_id = None
        while True:
            res = await ws.recv()
            obj = json.loads(res)
            if obj['type'] == 'message':
                message = Message(**obj['data'])
                if message.type == 'token':
                    result += message.msg
                    msg_id = message.id
                    continue
                else:
                    assert result == message.msg
                    assert 'hello' in message.msg
                    assert msg_id is not None
                    logging.debug(msg_id, message.id)
                    assert msg_id == message.id
                    break
    # 获取chats列表
    chats = get_chats(bot_id)
    assert len(chats) == 1
    chat_id = chats[0]['id']
    # 获取messages列表
    messages = get_messages(bot_id, chat_id)
    assert len(messages) == 2
    clear_bot(bot_id)

if __name__ == '__main__':
    asyncio.run(test_user_chat())