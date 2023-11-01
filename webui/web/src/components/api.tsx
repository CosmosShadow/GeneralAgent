// ```typescript
import axios, { AxiosResponse } from "axios";
import {Bot} from './interface'

const HOST = '127.0.0.1:7777'

export const HTTP_HOST = 'http://' + HOST;
export const WS_HOST = 'ws://' + HOST;


const header = {
  headers: {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  },
};

export async function apiSendCode(phone: string, randstr: string, ticket: string): Promise<AxiosResponse> {
  const url = `${HTTP_HOST}/user/send_code`;
  const data = {
    'phone': phone,
    'randstr': randstr,
    'ticket': ticket
  };
  const response = await axios.post(url, data, header);
  return response;
}

export async function apiBotList(): Promise<AxiosResponse> {
  const url = `${HTTP_HOST}/bot/list`;
  const response = await axios.get(url);
  return response;
}

export async function apiChatList(bot_id:string): Promise<AxiosResponse> {
  const url = `${HTTP_HOST}/chats/${bot_id}`;
  const response = await axios.get(url);
  return response;
}

// @app.post('/clear/{bot_id}')
// 清空聊天记录
export async function apiChatClear(bot_id:string): Promise<AxiosResponse> {
  const url = `${HTTP_HOST}/clear/${bot_id}`;
  const response = await axios.post(url);
  return response;
}

export async function apiChatListNew(bot_id:string): Promise<AxiosResponse> {
  const url = `${HTTP_HOST}/chats/new/${bot_id}`;
  const response = await axios.get(url);
  return response;
}

export async function apiMessages(bot_id: string, chat_id: string): Promise<AxiosResponse> {
  const url = `${HTTP_HOST}/messages/`;
  const data = {
    bot_id: bot_id,
    chat_id: chat_id
  };
  const response = await axios.post(url, data);
  return response;
}

// export async function apiUploadFile(bot_id: string, chat_id: string, file: File): Promise<string> {
//   const url = `${HTTP_HOST}/file/upload`;
//   const formData = new FormData();
//   formData.append("bot_id", bot_id);
//   formData.append("chat_id", chat_id);
//   formData.append("file", file);
//   const response = await axios.post(url, formData);
//   if (response.status !== 200 || response.data.code !== 0) {
//     throw new Error("Upload file failed.");
//   }
//   return response.data.file;
// }

export async function apiUploadFile(bot_id: string, chat_id: string, file: File): Promise<string> {
  const url = `${HTTP_HOST}/file/upload`;
  const formData = new FormData();
  formData.append("bot_id", bot_id);
  formData.append("chat_id", chat_id);
  formData.append("file", file);
  const response = await axios.post(url, formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  if (response.status !== 200 || response.data.code !== 0) {
    throw new Error("Upload file failed.");
  }
  return response.data.file;
}

export async function apiDownloadURL(file_path: string): Promise<string> {
  const url = `${HTTP_HOST}/file/download`;
  const data = {
    file_path: file_path
  }
  const response = await axios.post(url, data);
  if (response.status !== 200 || response.data.code !== 0) {
    throw new Error("Download file failed.");
  }
  return response.data.url;
}

export const get_chat_file_url = (bot_id: string, chat_id:string, file_name:string) =>{
  const url = `${HTTP_HOST}/file/download/${bot_id}/${chat_id}/${file_name}`;
  return url
}

export const default_application_avator = process.env.PUBLIC_URL + "/products/default_bot.png"
export const defualt_user_avator = process.env.PUBLIC_URL + "/products/default_user.png"

export const get_application_icon_src = (bot: Bot|null) => {
  if (bot && bot.id == 'app_store') {
    return process.env.PUBLIC_URL + "/products/app_store.jpeg"
  }
  if (bot && bot.id == 'personal_setting') {
    return process.env.PUBLIC_URL + "/products/personal_setting.jpeg"
  }

  if (bot && bot.icon_url) {
    let icon_url = `${HTTP_HOST}/system/file/${bot.icon_url}`
    return icon_url
  } else {
    return default_application_avator
  }
}

export const get_system_file = (file_path:string) => {
  return `${HTTP_HOST}/system/file/${file_path}`
}

export const get_public_image_src = (image_url: string) => {
  let image_src = `${HTTP_HOST}/public/images/${image_url}`
  return image_src
}