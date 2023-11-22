import React, { useContext, useEffect, useState, useRef} from 'react'
import {Message, Bot} from './interface';
import DynamicUI from './dynamic_ui';
import { message, Button} from 'antd';
import {get_system_file} from './api'
import { WebSocketContext } from './WebSocketContext';
import Lib06f4 from './Lib06f4';
import {FileUploadButton, withChatAndBotId} from './file_upload_button';

interface Props {
    bot: Bot;
    chat_id: string;
}

const UIApplication: React.FC<Props> = (props) => {
    const { sendMessage, subscribe } = useContext(WebSocketContext);
    const bot = props.bot


    const lib_name = bot.js_name as string
    const js_url = get_system_file(bot.js_path as string)
    // const data = ui_dict['data']

    const save_data = (user_data:any) => {
        const mes: Message = {
            bot_id: bot.id,
            chat_id: props.chat_id,
            msg: JSON.stringify({'data': user_data}),
            type: 'message',
        }
        sendMessage(JSON.stringify({
			'type': 'message',
			'data': mes
		}));
    }

    const NewFileUploadButton = withChatAndBotId(bot.id as string, props.chat_id)(FileUploadButton);

    return (
        // <DynamicUI name={lib_name} js_url={js_url} data={null} save_data={save_data}/>
        <Lib06f4 save_data={save_data} FileUploadConponent={NewFileUploadButton}/>
    );
}

export default UIApplication;
