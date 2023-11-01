import React, { useEffect, useState, useRef} from 'react'
import {Message} from './interface';
import DynamicUI from './dynamic_ui';
import { message, Button} from 'antd';
import {get_chat_file_url} from './api'

interface Props {
    message: Message;
}

const UIMesasge: React.FC<Props> = (props) => {
    const message = props.message
    const ui_dict = JSON.parse(props.message.ui as string)
    const lib_name = ui_dict['name']
    const js_path = ui_dict['js']
    const js_url = get_chat_file_url(message.bot_id as string, message.chat_id as string, js_path)
    const data = ui_dict['data']
    return (
        <DynamicUI name={lib_name} js_url={js_url} data={data}/>
    );
}

export default UIMesasge;
