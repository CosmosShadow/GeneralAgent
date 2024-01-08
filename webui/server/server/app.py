import os
import asyncio
import random
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, Depends, File, UploadFile, HTTPException, WebSocketDisconnect, Query, Request, BackgroundTasks, Form, Path
from fastapi.responses import RedirectResponse, Response, FileResponse
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from tinydb import TinyDB, Query
from dotenv import load_dotenv
import threading
import logging
import queue
import uuid
import uuid, json
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

# Try to set DATA_DIR
data_dir = os.environ.get('DATA_DIR', None)
if data_dir is None:
    the_dir = os.path.join(os.path.dirname(__file__), '../../../data/')
    # logging.info('enviroment DATA_DIR (user data directory) is not set, use default: %s', the_dir)
    # print('enviroment DATA_DIR (user data directory) is not set, use default: %s' % the_dir)
    os.environ['DATA_DIR'] = the_dir

from GeneralAgent import skills
from GeneralAgent.utils import set_local_applications_dir, set_tsx_builder_dir
from GeneralAgent.utils import set_logging_level, get_server_dir, get_applications_data_dir
set_logging_level(os.environ.get('LOG_LEVEL', 'ERROR'))
set_tsx_builder_dir(os.path.join(os.path.dirname(__file__), 'ts_builder'))
set_local_applications_dir(os.path.join(os.path.dirname(__file__), 'applications'))

# load env
# if os.path.exists('.env'):
#     load_dotenv('.env')

import contextvars
import functools
async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)

@dataclass
class Chat():
    id: Optional[str] = None
    name: Optional[str] = ''
    create_at: Optional[str] = None
    update_at: Optional[str] = None
    bot_id: Optional[str] = ''

    def __post_init__(self):
        if self.create_at is None:
            self.create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        if self.update_at is None:
            self.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        if self.id is None:
            self.id = datetime.now().strftime("%Y%m%d_%H%M%S") + '_' + str(uuid.uuid4())[:8]


@dataclass
class Message():
    type: Optional[str] = 'message' # token | message
    id: Optional[str] = None
    role: Optional[str] = ''               # user / bot
    bot_id: Optional[str] = ''           # bot id
    chat_id: Optional[str] = ''          # chat id
    create_at: Optional[str] = None
    msg: Optional[str] = ''
    file: Optional[str] = ''
    ui: Optional[str] = ''      # UI组件(js, name, data)
    extention: Optional[str] = None     # 扩展字段

    def __post_init__(self):
        if self.create_at is None:
            self.create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        if self.id is None:
            self.id = str(uuid.uuid4())

    def response_template(self, is_token=False):
        new_message = Message(
            role='bot',
            bot_id=self.bot_id,
            chat_id=self.chat_id,
            type='token' if is_token else 'message',
        )
        return new_message
    
    def to_text(self):
        data = {
            'type': 'message',
            'data': self.__dict__
        }
        return json.dumps(data)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_path = os.path.join(get_server_dir(), './general_agent_db.json')
db = TinyDB(db_path)
task_queue: queue.Queue = queue.Queue()
response_queue: queue.Queue = queue.Queue()


def sync_worker():
    asyncio.run(worker())

applications_data_dir = get_applications_data_dir()

def get_bot_dir(bot_id):
    """
    Return the bot data dir
    """
    data_dir = os.path.join(applications_data_dir, bot_id)
    return data_dir

def get_chat_dir(bot_id, chat_id):
    """
    Return the chat data dir
    """
    data_dir = os.path.join(applications_data_dir, bot_id, chat_id)
    return data_dir


def history_to_messages(history):
    messages = []
    for item in history:
        message = Message(**item)
        role = {'user': 'user', 'bot': 'assistant'}.get(message.role, 'user')
        content = message.msg if len(message.msg) > 0 else message.file
        messages.append({'role': role, 'content': content})
    return messages

def try_create_chat_name(message:Message, chat_messages):
    from GeneralAgent import skills
    chat = db.table('chats').get(Query().id == message.chat_id)
    chat = Chat(**chat)
    if chat.name == '' and len(chat_messages) > 0:
        content = chat_messages[0]['content']
        if len(content) < 10:
            title = content
        else:
            language = os.environ.get('LLM_RESPONSE_LANGUAGE', 'english')
            title = skills.extract_title(content, language=language)
        chat.name = title
        db.table('chats').update({'name': title}, Query().id == message.chat_id)

async def worker():
    logging.info('enter worker')
    while True:
        try:
            message = None
            current_workspace_dir = None
            # message:Message = await to_thread(task_queue.get)
            while True:  # Add a loop here
                try:
                    message: Message = await to_thread(task_queue.get_nowait)
                    break  # If the message is successfully got, break the loop
                except queue.Empty:
                    # if random.random() < 0.01:
                    #     logging.info('Worker waiting for a message.')
                    await asyncio.sleep(0)  # Wait for a while before the next attempt
            logging.info('Worker get a message')
            chat_id = message.chat_id
            bot_id = message.bot_id
            msg_id = str(uuid.uuid4())
            result = ''

            def _output_callback(token):
                nonlocal result
                nonlocal msg_id
                if token is not None:
                    result += token
                    # logging.debug({'token': token})
                    response:Message = message.response_template(is_token=True)
                    response.msg = token
                    response.id = msg_id
                    response_queue.put(response)
                    # await to_thread(response_queue.put, response)
                else:
                    if len(result.strip()) > 0:
                        response:Message = message.response_template()
                        response.msg = result.strip()
                        response.id = msg_id
                        save_message(response)
                        # await to_thread(response_queue.put, response)
                        response_queue.put(response)
                        result = ''
                        msg_id = str(uuid.uuid4())
                        logging.info('sended message')

            async def _file_callback(file_path):
                file_path = skills.try_download_file(file_path)
                response:Message = message.response_template()
                response.file = file_path
                save_message(response)
                # await to_thread(response_queue.put, response)
                response_queue.put(response)
                logging.info('sended file')

            # async def _ui_callback(name, js_path, data={}):
            #     """
            #     Send UI to user, name: UI component name, js_path: js file address corresponding to UI component, data: data required by UI component
            #     """
            def send_ui(component_name:str, js_path:str, data={}):
                """
                Send UI to user, component_name: UI component name, js_path: js file address corresponding to UI component, data: data required by UI component
                """
                response:Message = message.response_template()
                response.ui = json.dumps({
                    'name': component_name,
                    'js': js_path,
                    'data': data
                })
                save_message(response)
                # await to_thread(response_queue.put, response)
                response_queue.put(response)
                logging.debug(response)
            
            # os.chdir(self.local_dir)
            current_workspace_dir = os.getcwd()
            application_module = skills.get_application_module(bot_id)
            db.table('mesasges').clear_cache()
            history = db.table('messages').search((Query().bot_id == bot_id) & (Query().chat_id == chat_id))[-20:]
            chat_messages = history_to_messages(history)

            bot_meta = skills.load_bot_metadata_by_id(bot_id)

            bot_is_agent = bot_meta.get('type', 'agent') == 'agent'
            if bot_is_agent:
                try_create_chat_name(message, chat_messages)

        
            # data_dir = os.path.join(os.getcwd(), 'data', bot_id, chat_id)
            data_dir = get_chat_dir(bot_id, chat_id)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            os.chdir(data_dir)
            if application_module is not None:
                # file = None if message.file == '' else message.file
                files = json.loads(message.file) if message.file != '' else []
                cache_key = f'{bot_id}_{chat_id}'
                cache = skills._get_cache(cache_key)
                cache_todo = application_module.main(cache, chat_messages, message.msg, files, _output_callback)
                skills._set_cache(cache_key, cache_todo)
                if len(result.strip()) > 0:
                    response = message.response_template()
                    response.msg = result
                    response.id = msg_id
                    save_message(response)
                    await to_thread(response_queue.put, response)
            else:
                response = message.response_template()
                response.msg = 'application load error'
                save_message(response)
                # await response_queue.put(response)
                await to_thread(response_queue.put, response)
        except Exception as e:
            logging.exception(e)
            if message is not None:
                response = message.response_template()
                response.msg = str(e)
                save_message(response)
                await to_thread(response_queue.put, response)
        finally:
            if message is not None:
                task_queue.task_done()
                logging.info('Worker process message successfully')
            if current_workspace_dir is not None:
                os.chdir(current_workspace_dir)

@app.on_event("startup")
async def startup_event():
    logging.info('startup')
    threading.Thread(target=sync_worker, daemon=True).start()

@app.on_event('shutdown')
async def shutdown_event():
    logging.info('shutdown')
    os._exit(0)

def save_message(message:Message):
    if message.chat_id == '':
        chat = Chat(
            bot_id=message.bot_id,
        )
        db.table('chats').insert(chat.__dict__)
        message.chat_id = chat.id
    # OpenAI Model like to save data in /mnt/data, but we need to save it in ./
    message.msg = message.msg.replace('/mnt/data/', './')
    db.table('messages').insert(message.__dict__)


async def listen_message(websocket: WebSocket) -> None:
    while True:
        # message = await response_queue.get()
        # message:Message = await to_thread(response_queue.get)
        # await websocket.send_text(message.to_text())
        # response_queue.task_done()
        try:
            message: Message = await to_thread(response_queue.get_nowait)
            await websocket.send_text(message.to_text())
            response_queue.task_done()
        except queue.Empty:
            # if random.random() < 0.01:
            #     logging.info('Socket waiting for a message.')
            await asyncio.sleep(0)


@app.websocket("/ws/user/")
async def websocket_user_endpoint(websocket: WebSocket):
    await websocket.accept()
    listen_task = asyncio.create_task(listen_message(websocket))
    try:
        while True:
            data = await websocket.receive_text()
            if data == 'ping':
                await websocket.send_text('pong')
                continue
            else:
                data = json.loads(data)
                logging.info('Websocket get a message')
                logging.info(data)
                if data['type'] == 'message':
                    message = Message(**data['data'])
                    message.role = 'user'
                    save_message(message)
                    logging.info(message.to_text())
                    await websocket.send_text(message.to_text())
                    logging.info('Websocket sended message')
                    await to_thread(task_queue.put, message)
                    # await task_queue.put(message)
    except Exception as e:
        if isinstance(e, WebSocketDisconnect):
            logging.info(f"websocket disconnect: {e}")
        else:
            logging.exception(e)
    finally:
        listen_task.cancel()
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close(code=4001)
            except:
                pass

@app.get("/bot/list")
async def bot_list():
    from GeneralAgent import skills
    return skills.load_applications()


@app.get("/chats/{bot_id}")
async def user_chat(bot_id: str):
    chats = db.table('chats').search(Query().bot_id == bot_id)
    # 当chats为空的时候，创建一个
    if len(chats) == 0:
        chat = Chat(
            bot_id=bot_id,
        )
        db.table('chats').insert(chat.__dict__)
        chats = db.table('chats').search(Query().bot_id == bot_id)
    # 倒序排列
    chats = chats[::-1]
    return chats

@app.get("/chats/new/{bot_id}")
async def user_chat_new(bot_id: str):
    chat = Chat(
        bot_id=bot_id,
    )
    db.table('chats').insert(chat.__dict__)
    chats = db.table('chats').search(Query().bot_id == bot_id)
    chats = chats[::-1]
    return chats


@app.post('/clear_bot_chats/{bot_id}')
async def clear_messages(bot_id: str):
    """
    clear all chats for bot
    """
    # clear messages
    db.table('messages').remove(Query().bot_id == bot_id)
    db.table('chats').remove(Query().bot_id == bot_id)
    # delete bot dir
    the_dir = get_bot_dir(bot_id)
    if os.path.exists(the_dir):
        import shutil
        shutil.rmtree(the_dir)
    return 'ok'


@app.post('/delete_chat/{bot_id}/{chat_id}')
async def delete_chat(bot_id: str, chat_id: str):
    """
    delete a chat
    """
    db.table('messages').remove((Query().bot_id == bot_id) & (Query().chat_id == chat_id))
    db.table('chats').remove((Query().bot_id == bot_id) & (Query().id == chat_id))
    # delete chat dir
    the_dir = get_chat_dir(bot_id, chat_id)
    if os.path.exists(the_dir):
        import shutil
        shutil.rmtree(the_dir)
    return 'ok'


class MessagesInput(BaseModel):
    bot_id: str
    chat_id: str
@app.post("/messages/")
async def user_messages(data:MessagesInput):
    bot_id = data.bot_id
    chat_id = data.chat_id
    db.table('mesasges').clear_cache()
    messages = db.table('messages').search((Query().bot_id == bot_id) & (Query().chat_id == chat_id))
    # print(messages)
    for message in messages:
        message['msg'] = message['msg'].replace('/mnt/data/', './')
    # print(messages)
    return messages

# @app.get("/system/file/{path:path}")
# async def get_file(path: str):
#     print(path)
#     if os.path.exists(path):
#         return FileResponse(path)
#     else:
#         raise HTTPException(status_code=404, detail="File not found")

@app.get("/system/file/")
async def get_file(path: str):
    decoded_path = os.path.normpath(path)  # 标准化路径，防止安全问题
    if os.path.exists(decoded_path):
        return FileResponse(decoded_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/file/download/{bot_id}/{chat_id}/{file_name:path}")
async def download_file(bot_id: str, chat_id: str, file_name: str = Path(..., convert_underscores=False)):
    the_dir = get_chat_dir(bot_id, chat_id)
    file_path = os.path.join(the_dir, file_name)
    # print(file_path)
    logging.debug(file_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")


# 文件上传: /file/upload
@app.post("/file/upload")
async def upload_file(
    bot_id: str = Form(..., description="Bot ID"),
    chat_id: str = Form(..., description="Chat ID"),
    file: UploadFile = File(...)
    ):
    file_name = file.filename
    the_dir = get_chat_dir(bot_id, chat_id)
    if not os.path.exists(the_dir):
        os.makedirs(the_dir)
    file_path = os.path.join(the_dir, file_name)
    with open(file_path, 'wb') as f:
        f.write(file.file.read())
    return {'code': 0, "message": "File uploaded successfully", 'file': './'+file_name}