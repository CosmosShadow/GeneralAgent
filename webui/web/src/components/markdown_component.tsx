import React from 'react';
import { get_chat_file_url } from './api';
import { Message } from './interface';
import { message } from 'antd';
import ImageComponent from './image_component'
import FileDownloadCompoent from './file_download'


type LinkObject = {
    type: 'text' | 'image' | 'file',
    title: string,
    url: string
  };
  
function splitStringWithLinks(str: string): LinkObject[] {
const regex = /(\[.*?\]\(sandbox:\/[^\)]+\))|(\!\[.*?\]\(sandbox:\/[^\)]+\))|([^!]\[.*?\]\(sandbox:\/[^\)]+\))/g; // 匹配 [xxx](sandbox:xxx) 和 ![xx](sandbox:xxx) 格式的链接
const matches = str.match(regex);
const result: LinkObject[] = [];

if (matches) {
    let lastIndex = 0;
    matches.forEach((match) => {
    const index = str.indexOf(match, lastIndex);
    const textBefore = str.slice(lastIndex, index);
    if (textBefore) {
        result.push({
        type: 'text',
        title: textBefore,
        url: ''
        });
    }
    if (match.startsWith('!')) {
        result.push({
        type: 'image',
        title: match.match(/\[(.*?)\]/)![1],
        url: match.match(/\(sandbox:\/([^\)]+)\)/)![1]
        });
    } else {
        // 文件结尾是图片格式，type切换成为图片
        const url = match.match(/\(sandbox:\/([^\)]+)\)/)![1]
        if (url.endsWith('.png') || url.endsWith('.jpg') || url.endsWith('.jpeg') || url.endsWith('.gif')) {
            result.push({
                type: 'image',
                title: match.match(/\[(.*?)\]/)![1],
                url: url
            });
        } else {
            result.push({
                type: 'file',
                title: match.match(/\[(.*?)\]/)![1],
                url: url
                });
        }
        
    }
    lastIndex = index + match.length; // 更新 lastIndex
    });
    const textAfter = str.slice(lastIndex);
    if (textAfter) {
    result.push({
        type: 'text',
        title: textAfter,
        url: ''
    });
    }
} else {
    result.push({
    type: 'text',
    title: str,
    url: ''
    });
}
return result;
}
  
// const input = "I have generated an image of a kitten. You can view the image [here](sandbox:/1edbedad2501.jpg) or ![here](sandbox:/another.jpg). Hello world";
// const result = splitStringWithLinks(input);
// console.log(result);

interface Props {
    message: Message
}


const MarkdownComponent: React.FC<Props> = (props) => {
    const message = props.message
    const links = splitStringWithLinks(props.message.msg?.trim() as string)
    // console.log(props.message.msg)
    // console.log(links)
    return (<div style={{ whiteSpace: 'pre-wrap' }} >{
        links.map((item, index)=>{
        // console.log(item)
        if (item.type === 'text') {
            return (<span key={index}>{item.title}</span>)
        } else if (item.type === 'image') {
            return (<span><br/><ImageComponent image_url={get_chat_file_url(message.bot_id as string, message.chat_id as string, item.url)} /></span>)
        } else {
            return (<span>&nbsp; <FileDownloadCompoent file_path={get_chat_file_url(message.bot_id as string, message.chat_id as string, item.url)} title={item.title}/>&nbsp;</span>)
        }
    })
    }</div>)
  };

export default MarkdownComponent;


