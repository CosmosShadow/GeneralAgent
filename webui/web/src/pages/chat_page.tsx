// import 'github-markdown-css'
import React, { useEffect, useState, useRef} from 'react'
//@ts-ignore
import Center from 'react-center';
import { Layout, Tooltip, Popover, Menu, Avatar, Button, Image, Input, List, message as antd_message, Col, Row, Divider, Popconfirm} from 'antd';
import {useSelector, useDispatch } from 'react-redux'
import {delete_bot, open_bot, top_bot} from '../db/redux'
import {Bot, Chat, block_bot_ids, theme_blue, cut_string} from '../components/interface'
import {get_application_icon_src} from '../components/api';
import BotList from '../components/bot_list';
import ChatList from '../components/chat_list';
import AppStore from '../components/app_store';
import PersonalSetting from '../components/personal_setting';
import ImageComponentPublic from '../components/image_component_public'
import ChatBox from '../components/chat_box';

import {
	DeleteOutlined,
  } from '@ant-design/icons';

const { Sider, Content } = Layout;

export default function ChatPage () {
	const dispatch = useDispatch();
	const current_bot: Bot = useSelector((state) => (state as any).data.current_bot);
	const [chat_id, setChatID] = useState(''); // Chat
	
	const onHandleSelectBot = (bot: Bot) => {
		console.log('onHandleSelectBot', bot)
		dispatch(open_bot(bot));
		setChatID('')
	}
	
	const onHandleDeleteCurrentBot = () => {
		dispatch(delete_bot(current_bot));
		setChatID('')
	}

	const onHandleSelectChat = (chat: Chat) => {
		setChatID(chat.id);
	}

	var contentDiv = null;
	if (current_bot && current_bot.id === 'app_store') {
		contentDiv = (<div style={{height: 'calc(100vh - 80px)', overflow: 'scroll' }}><AppStore onHandleSelectBot={onHandleSelectBot}/></div>)
	} else if (current_bot && current_bot.id === 'personal_setting') {
		contentDiv = (<div style={{height: 'calc(100vh - 80px)', overflow: 'scroll' }}><PersonalSetting onHandleSelectBot={onHandleSelectBot}/></div>)
	} else  {
		contentDiv = chat_id != '' && (<ChatBox can_upload_file={current_bot.upload_file === 'yes'} bot_id={current_bot.id} chat_id={chat_id} />);
	}

	return (
		<div style={{background: '#F0F0F0', overflow: 'hidden'}} className='ChatDiv'>
		{/* <SocketComponent socketRef={socketRef} setTmpMessageDict={setTmpMessageDict} /> */}
		<Center>
			<div style={{width: '1400px', height: '100vh'}}>
			<Layout>
			<Sider style={{background: theme_blue, height: '100vh'}}>
				<div style={{padding: 20, background: theme_blue, fontWeight: 'bold', height: 60, fontSize: 18, color: 'white'}}>General Agent</div>
				<div style={{overflow: 'scroll', height: 'calc(100vh - 70px)', background: theme_blue}}><BotList onHandleSelectBot={onHandleSelectBot}/></div>
			</Sider>
			<Content style={{ padding: '0px',  background: '#F0F0F0', height: '100vh'}}>
			<div style={{display:'flex', justifyContent:'space-between', padding: 7, height: 60, background: '#309ee9', color: 'white'}}>
				<div style={{ display: 'flex', alignItems: 'center', marginLeft: 4 }}>
					{current_bot && current_bot.icon_url && 
						<ImageComponentPublic 
							src={get_application_icon_src(current_bot)} 
							style={{ 
								width: '46px',
								marginRight: '10px', 
								alignSelf: 'flex-start',
								borderRadius: '23%',
							}} 
						/>
					}
					<div style={{ textAlign: 'left'}}>
						<b>{current_bot ? current_bot.nickname : ''}</b>
						<div style={{ fontSize: 12, paddingTop: 3 }}>
						<Tooltip color='cyan' title={current_bot && current_bot.description.length > 150 ? current_bot.description : ''}>
							<span>{current_bot ? cut_string(current_bot.description, 150) : ''}</span>
						</Tooltip>
						</div>
					</div>
				</div>
				{current_bot && (!block_bot_ids.includes(current_bot.id)) && 
					<div style={{paddingTop: 10}}>
						<Button type='link' onClick={onHandleDeleteCurrentBot}><DeleteOutlined style={{color: 'white', fontSize: 16}}/></Button>
					</div>
				}
			</div>
			<Center>
				<div style={{width: '1000px', paddingTop: 20, padding: 10, background: '#FFFFFF'}}>
					{contentDiv}
				</div>
			</Center>
		</Content>
		<Sider style={{height: '100vh', background: '#F0F0F0'}} width={200}>
			<div style={{padding: 20, fontWeight: 'bold', height: 20, fontSize: 18, color: 'black'}}></div>
			<div style={{overflow: 'scroll', height: 'calc(100vh - 70px)', background: '#F0F0F0'}}>
				<ChatList onHandleSelectChat={onHandleSelectChat} bot={current_bot}/>
			</div>
		</Sider>
		</Layout>
		</div>
		</Center>
	</div>
	);
};