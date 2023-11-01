import {useSelector, useDispatch } from 'react-redux'
import {update_bot_list, open_bot, top_bot} from '../db/redux'
import React, { useEffect, useState, useRef} from 'react'
import {  List } from 'antd';
import {Bot, app_store_bot, personal_setting_bot} from '../components/interface'
import ImageComponentPublic from './image_component_public'
import {get_application_icon_src} from './api'

export default function BotList ({ onHandleSelectBot }: { onHandleSelectBot: (bot: Bot) => void }) {
    const bot_list = useSelector((state) => (state as any).data.bot_list);
    const dispatch = useDispatch();
    const current_bot: Bot = useSelector((state) => (state as any).data.current_bot);

    const bot_list_with_app_store = [app_store_bot, personal_setting_bot,  ...bot_list]

    // 获取bot列表
	const getBotList = async () => {
		// console.log('getBotList');
		// apiBotListLike().then(function(res){
        //     const new_bot_list = res.data;
		// 	dispatch(update_bot_list(new_bot_list));
		// });
	}

    useEffect(() => {
		getBotList();
		return () => {
		};
	  }, []); // 添加空数组作为依赖

    return (
    <List
        itemLayout="horizontal"
        dataSource={bot_list_with_app_store.map((bot: Bot) => ({
            ...bot,
            selected: current_bot && (current_bot['id'] === bot['id'])
        }))}
        renderItem={(bot: any, index) => (
            <List.Item 
                key={index} 
                style={{ 
                    backgroundColor: bot.selected ? '#FFFFFF' : undefined, 
                    color: bot.selected ? '#000000' : '#FFFFFF',
                    height: 50,
                    textAlign: 'left',
                    paddingLeft: 0,
                    fontWeight: 'bold',
                    width: 200,
                    cursor: 'pointer',
                }} 
                onClick={() => onHandleSelectBot(bot)}
            >
                <ImageComponentPublic 
                    src={get_application_icon_src(bot)} 
                    style={{ 
                        width: '30px',
                        marginRight: '10px', 
                        marginLeft: '10px', 
                        // alignSelf: 'flex-start',
                        borderRadius: '23%',
                        backgroundColor: '#FFFFFF',
                    }} 
                />
                <div style={{ textAlign: 'left', width: 140, marginTop: 0, marginRight: 10}}>{bot.nickname}</div>
            </List.Item>
        )}
    />)
}