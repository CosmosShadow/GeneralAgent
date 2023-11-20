// 机器人
export interface Bot {
    id: string;
    name: string;
    nickname: string;
    description: string;
    tags: string[];
    icon_url?: string;
    upload_file?: string;
    type?: string;
    js_name?: string,
    js_path?: string,
}

// Chat
export interface Chat {
  id: string, 
  name: string,
  create_at: string
}

// 消息
export interface Message {
  type: string; // token、message
  id?: string;
  bot_id?: string;
  chat_id?: string;
  role?: string;
  send_name?: string;
  create_at?: string;
  msg?: string;
  file?: string;
  ui?: string;
  extention?: string;
  }

export const theme_blue = '#108ee9';

export const app_store_bot: Bot = {id: 'app_store', name: 'app_store', nickname: 'Agent Store', description: 'select one to use', tags: [], icon_url: 'app_store.jpeg'};
export const personal_setting_bot: Bot = {id: 'personal_setting', name: 'personal_setting', nickname: 'Setting', description: 'change language, llm, theme and others', tags: [], icon_url: 'personal_setting.jpeg'};
export const block_bot_ids = [app_store_bot.id, personal_setting_bot.id]

export const cut_string = (str: string, len: number) => {
  return str.length > len ? str.substring(0, len).concat("...") : str
}