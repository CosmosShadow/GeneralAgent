import React, { useContext, useEffect, useState, useRef} from 'react'
import {Message} from './interface';
import DynamicUI from './dynamic_ui';
import {get_chat_file_url} from './api'
import { WebSocketContext } from './WebSocketContext';

interface Props {
    message: Message;
}

const UIMesasge: React.FC<Props> = (props) => {
    const { sendMessage, subscribe } = useContext(WebSocketContext);
    const message = props.message
    const ui_dict = JSON.parse(props.message.ui as string)
    const lib_name = ui_dict['name']
    const js_path = ui_dict['js']
    const js_url = get_chat_file_url(message.bot_id as string, message.chat_id as string, js_path)
    const data = ui_dict['data']

    const save_data = (user_data:any) => {
        const mes: Message = {
            bot_id: message.bot_id,
            chat_id: message.chat_id,
            msg: JSON.stringify({'data': user_data}),
            type: 'message',
        }
        sendMessage(JSON.stringify({
			'type': 'message',
			'data': mes
		}));
    }

    return (
        <DynamicUI name={lib_name} js_url={js_url} data={data} save_data={save_data}/>
    );
}

export default UIMesasge;
