import uuid, json
from typing import Optional
from datetime import datetime
from dataclasses import dataclass


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