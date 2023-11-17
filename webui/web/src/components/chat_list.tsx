import React, { useEffect, useState} from 'react'
import { List, Button, Popconfirm} from 'antd';
import {Bot, Chat, cut_string} from '../components/interface'
import {apiChatList, apiChatListNew, apiChatClear, apiDeleteChat} from '../components/api'

interface Props {
    onHandleSelectChat: (chat: Chat) => void;
    bot: Bot;
  }

export default function ChatList (props: Props) {
    const [chat_list, setChatList] = useState([]); // [Chat
    const [current_chat, setCurrentChat] = useState(null); // Chat

	const getChatList = async () => {
		apiChatList(props.bot.id).then(function(res){
            setChatList(res.data);
            // console.log(res.data)
            onHandleSelectChat(res.data[0])
		});
	}

    const onHandleSelectChat = (chat: Chat) => {
        setCurrentChat(chat as any);
        props.onHandleSelectChat(chat)
    }

    const onhandleNewChat = () => {
        apiChatListNew(props.bot.id).then(function(res){
            setChatList(res.data);
            // console.log(res.data)
            onHandleSelectChat(res.data[0])
        });
    }

    const onhandleClearAll = () => {
        apiChatClear(props.bot.id).then(function(res){
            setChatList([]);
            // console.log(res.data)
            // onHandleSelectChat(null)
            onhandleNewChat()
        });
    }

    const onHandleDeleteChat = (chat_id: string) => {
        apiDeleteChat(props.bot.id, chat_id).then(function(res){
            setChatList((chat_list as any).filter((chat: Chat) => chat.id !== chat_id));
            // 自动选择删除后的第一个或者前一个呢
            const index = (chat_list as any).findIndex((chat: Chat) => chat.id === chat_id);
            // console.log(index);
            if (index > 0) {
                onHandleSelectChat((chat_list as any)[index - 1])
            } else if (index === 0 && (chat_list as any).length > 1) {
                onHandleSelectChat((chat_list as any)[1])
            } else {
            }
        });
    }

    useEffect(() => {
        if (props.bot) {
            getChatList();
        }
	  }, [props.bot]); 

    if (props.bot && props.bot.id && (props.bot.id == 'app_store' || props.bot.id == 'personal_setting')) {
        return null;
    }

    return (
    <>
    <div style={{marginBottom: 20}}>
        <Button onClick={onhandleNewChat} type='primary'>New Chat</Button>
    </div>
    <List
        itemLayout="horizontal"
        dataSource={chat_list.map((chat: Chat) => ({
            ...chat,
            selected: current_chat && (current_chat['id'] === chat['id'])
        }))}
        renderItem={(chat: any, index) => (
            <List.Item 
                key={index} 
                style={{ 
                    backgroundColor: chat.selected ? '#FFFFFF' : undefined, 
                    color: chat.selected ? 'red' : 'green',
                    height: 40,
                    textAlign: 'left',
                    paddingLeft: 10,
                    marginLeft: 0,
                    // fontWeight: 'bold',
                    width: 200,
                    cursor: 'pointer',
                }} 
                onClick={() => onHandleSelectChat(chat)}
            >
                <div style={{ textAlign: 'left', width: 200, marginTop: 0, marginRight: 0}}><a>{(chat.name && cut_string(chat.name, chat.selected ? 15: 23)) || chat.create_at.slice(0, 16) }</a></div>
                {chat.selected && <div><Button type="link" onClick={()=>{onHandleDeleteChat(chat.id)}}>Del</Button></div>}
            </List.Item>
        )}
    />
    
    {/* <div style={{marginTop: 10}}>
        <Button onClick={onhandleNewChat}>Clear All</Button>
    </div> */}
    <div style={{height: 20}}></div>
    <Popconfirm
        title="Are you sure to delete all chats?"
        onConfirm={onhandleClearAll}
        okText="Yes"
        cancelText="No"
  >
    <a href="#">Clear All</a>
    {/* <Button >Clear All</Button> */}
  </Popconfirm>
    </>
    )
}