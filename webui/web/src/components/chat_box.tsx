import React, { useContext, useEffect, useState, useRef} from 'react'
//@ts-ignore
import Center from 'react-center';
import { Layout, Button, Input} from 'antd';
import {useSelector, useDispatch } from 'react-redux'
import {top_bot} from '../db/redux'
import {Bot, Message} from '../components/interface'
import {FileUploadButton} from '../components/file_upload_button'
import { ClearOutlined } from '@ant-design/icons';
import MessageList from '../components/message_list';
import {apiMessages} from '../components/api'
import { WebSocketContext } from './WebSocketContext';


const { TextArea } = Input;

interface Props {
    chat_id: string;
    bot_id: string;
	can_upload_file: boolean;
  }

const ChatBox : React.FC<Props> = (props) => {
	const dispatch = useDispatch();
	const [inputValue, setInputValue] = useState('');
	const [buttonCanClicked, setButtonCanClicked] = useState(false);
	const [messages, setMessages] = useState<Message[]>([]);
	const [tmpMessage, SetTmpMessage] = useState<Message | null>(null);
	const { sendMessage, subscribe } = useContext(WebSocketContext);

	const current_bot: Bot = useSelector((state) => (state as any).data.current_bot);
	const textAreaRef = useRef<any>(null);

	// console.log(props.chat_id)

	// 获取历史消息
	const getHistoryMessage = () => {
		apiMessages(props.bot_id, props.chat_id).then(function(res){
			setMessages(res.data);
		})
	}
	useEffect(() => {
		getHistoryMessage();
	}, [props.bot_id, props.chat_id]);

	const chatIDRef = useRef<string | null>(null);
	chatIDRef.current = props.chat_id;

	// 监听消息
	useEffect(() => {
		subscribe((message) => {
			// console.log(message)
			var obj = JSON.parse(message);
			if (obj['type'] == 'message') {
				const message_obj:Message = obj['data']
				// console.log(message_obj.bot_id)
				// console.log(props.bot_id)
				// console.log(message_obj.chat_id)
				// console.log(chatIDRef.current)
				if (message_obj.bot_id == props.bot_id && message_obj.chat_id == chatIDRef.current) {
					if (message_obj.type == 'token') {
						// console.log({'token': message_obj.msg});
						SetTmpMessage(tmpMessage =>{
							if (tmpMessage && tmpMessage.msg != null && tmpMessage.id == message_obj.id) {
								// console.log({'set token': message_obj.msg});
								const newMessageObj: Message = { ...message_obj }; // 复制一个新的message_obj对象
    							newMessageObj.msg = tmpMessage.msg + message_obj.msg; // 修改新对象的msg属性
								// console.log(newMessageObj)
    							return newMessageObj; // 返回新对象
							} else {
								return message_obj
							}
						})
					} else {
						SetTmpMessage(null)
						setMessages(messages => [...messages, message_obj]);
					}
				}
			}
		});
	  }, [subscribe]);

	const sendFile = (file_path: string) => {
		const message: Message = {
			type: 'message',
			bot_id: props.bot_id,
			chat_id: props.chat_id,
			msg: '',
			file: file_path,
		}
		sendMessage(JSON.stringify({
			'type': 'message',
			'data': message
		}));
		dispatch(top_bot(current_bot))
	}
	
	// 输入框聚焦
	useEffect(() => {
		if (textAreaRef.current) {
		  // Save current page scroll position
		  const x = window.scrollX;
		  const y = window.scrollY;
		  setTimeout(() => {
			// Apply the focus
			textAreaRef.current.focus();
			// Scroll back to the initial position
			window.scrollTo(x, y);
		  }, 100);
		}
	  }, [current_bot]);

	const onHandleSend = () => {
		var text = inputValue.trim()
		setInputValue('')
		const message: Message = {
			type: 'message',
			bot_id: props.bot_id,
			chat_id: props.chat_id,
			msg: text,
		}
		// console.log(props.chat_id)
		sendMessage(JSON.stringify({
			'type': 'message',
			'data': message
		}));
		dispatch(top_bot(current_bot))
	  };

	const onTextAreaChanged = (e: any) => {
		setInputValue(e.target.value)
		if (e.target.value.trim() === '') {
			setButtonCanClicked(false)
		} else {
			setButtonCanClicked(true)
		}
	}

	// console.log(tmpMessage?.msg);
	const is_application = current_bot.type == 'application';

	return (
	<div>
		<MessageList messages={messages as Message[]} tmp_message={tmpMessage} bot={current_bot} chat_id={props.chat_id}/>
		{!is_application && 
			<div style={{ height: '80px', display: 'flex', position: 'relative', marginBottom: 10, marginTop: 10}}>
				<div style={{width: 40, bottom: 47, position: 'absolute', left: 15}}>
					{props.can_upload_file && <FileUploadButton bot_id={props.bot_id} chat_id={props.chat_id} onUploadSuccess={sendFile}/>}
				</div>
				{/* <div style={{width: 40, bottom: 47, position: 'absolute', left: 75}}><Button><ClearOutlined /></Button></div> */}
				<TextArea
					ref={textAreaRef}
					autoSize={{ minRows: 1, maxRows: 20 }}
					value={inputValue}
					style={{ width: 760, bottom: 47, left: 90, position: 'absolute' }}
					placeholder='input...'
					onChange={onTextAreaChanged}
				/>
				<Button style={{width: 80, position: 'absolute', bottom: 47, left: 880}} type='primary' disabled={!buttonCanClicked} onClick={(e) => {onHandleSend()}}>Send</Button>
			</div>
		}
	
	</div>
	);
};

export default ChatBox