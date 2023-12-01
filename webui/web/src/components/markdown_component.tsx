import React from 'react';
import { get_chat_file_url } from './api';
import { Message } from './interface';
import { message } from 'antd';
import ImageComponent from './image_component'
import FileDownloadCompoent from './file_download'
import AudioPlayer from './audio_player';


type LinkObject = {
    type: 'text' | 'image' | 'file' | 'audio' | 'video',
    title: string,
    url: string
  };
  
  function splitStringWithLinks(str: string): LinkObject[] {
    const regex = /(!?\[.*?\]\((sandbox:\/?)?[^\)]+\))/g;
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
            const url = match.match(/\((sandbox:\/?)?([^\)]+)\)/)![2];
            if (match.startsWith('!') || url.endsWith('.png') || url.endsWith('.jpg') || url.endsWith('.jpeg') || url.endsWith('.gif')) {
                result.push({
                    type: 'image',
                    title: match.match(/\[(.*?)\]/)![1],
                    url: url
                });
            } else if (url.endsWith('.mp3') || url.endsWith('.wav')) {
                result.push({
                    type: 'audio',
                    title: match.match(/\[(.*?)\]/)![1],
                    url: url
                })
            } else if (url.endsWith('.mp4') || url.endsWith('.mov')) {
                result.push({
                    type: 'video',
                    title: match.match(/\[(.*?)\]/)![1],
                    url: url
                })
            } else {
                result.push({
                    type: 'file',
                    title: match.match(/\[(.*?)\]/)![1],
                    url: url
                });
            }
            lastIndex = index + match.length;
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
        } else if (item.url && item.url.startsWith('http')) {
            // 新开一个页面
            return (<span key={index}><a  target='_blank' href={item.url}>{item.title}</a></span>)
        } else {
            const url = get_chat_file_url(message.bot_id as string, message.chat_id as string, item.url);
            if (item.type === 'image') {
                return (<span key={index}><br/><ImageComponent image_url={url} /></span>)
            } else if (item.type == 'audio') {
                return (<span key={index}><FileDownloadCompoent file_path={url} title={item.title}/><AudioPlayer file={url}/></span>)
            } else if (item.type == 'video') {
                return (<span key={index}><FileDownloadCompoent file_path={url} title={item.title}/><br/><video controls src={url}></video><br/></span>)
            } else {
                return (<span key={index}><FileDownloadCompoent file_path={url} title={item.title}/></span>)
            }
        }
    })
    }</div>)
  };

export default MarkdownComponent;


