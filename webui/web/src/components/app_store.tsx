import React, { useState, useEffect } from 'react';
import {useSelector, useDispatch } from 'react-redux'
import { Input, Tooltip, Space, Button, Spin} from 'antd';
import { Row, Col, Avatar } from 'antd';
import {Bot, theme_blue, cut_string} from '../components/interface'
import {apiBotList, get_application_icon_src} from '../components/api'
import {update_app_store_bot_list} from '../db/redux'
import ImageComponentPublic from './image_component_public'

const { Search } = Input;

// const AppStore = () => {
export default function AppStore ({ onHandleSelectBot }: { onHandleSelectBot: (bot: Bot) => void }) {
    const dispatch = useDispatch();
    let tags_dict: {[key: string]: string} = {
        'all': '全部',
        'chat': 'Chat', 
        'hr': 'HR',
        'image': '图像',
        'video': '视频', 
        'audio': '音频',
        'person': '人物',
        'doc': '文档', 
        'develop': '开发',
        'language': '语言',
        'professional': '专业',
        'philosophy': '哲学',
        'write': '写作',
        'music': '音乐',
        'contribute': '建议',
        'seo': 'SEO',
        'pedagogy': '教育',
        'games': '游戏',
        'social': '社交',
        'interesting': '爱好',
        'life': '生活',
        'finance': '金融',
        'ai': 'AI',
        'doctor': '医生',
        'company': '公司',
        'living': '生活',
        'speech': '演讲',
        'academic': '学术',
        'comments': '评论',
        'mind': '思想',
        'tool': '工具',
        'article': '文章',
    }
    // 获取tags的所有key
    const tags_keys = Object.keys(tags_dict).map((key) => key);
    const local_bot_list = useSelector((state) => (state as any).data.app_store_bot_list);
    const [bot_list, setBotList] = useState(local_bot_list);
    // const [bot_list, setBotList] = useState([]);

    const [selectedTag, setSelectedTag] = useState('all');
    var init_loading = true
    if (local_bot_list && local_bot_list.length > 0) {
        init_loading = false
    }
    const [loading, setLoading] = useState(init_loading);

    const [bot_list_tags, setBotListTags] = useState([...bot_list]);
    const [bot_list_tags_filtered, setBotListTagsFiltered] = useState([...bot_list_tags]);

    // 获取bot列表
	const getBotList = async () => {
		// console.log('getBotList');
		apiBotList().then(function(res){
            // 过滤掉hello
            const new_bot_list = res.data.filter((bot: Bot) => {
                return bot && bot.id != 'hello';
            });
			dispatch(update_app_store_bot_list(new_bot_list));
            setBotList(new_bot_list)
            setBotListTags(new_bot_list);
            setBotListTagsFiltered(new_bot_list);
            setLoading(false);
		});
	}

    useEffect(() => {
		getBotList();
	  }, []); // 添加空数组作为依赖

    const onSearch = (e: any) => {
        let value = e.target.value;
		// setInputValue(e.target.value)
    // const onSearch = (value: string) => {
        console.log(value);
        // 过滤选中tag的bot list，并成为新的list，用于显示
        setBotListTagsFiltered(bot_list_tags.filter((bot: Bot) => {
            return bot.nickname.includes(value) || bot.description.includes(value)
        }));
    };

    const handleTagClick = (tag: string) => {
        setSelectedTag(tag);
        let new_bot_list = [];
        if (tag == 'all') {
            new_bot_list = [...bot_list]
        } else {
            new_bot_list = bot_list.filter((bot: Bot) => {
                // console.log(bot)
                // console.log(bot.tags)
                return bot.tags.includes(tag);
            })
        }
        setBotListTags(new_bot_list);
        setBotListTagsFiltered(new_bot_list);
        // console.log(`Selected tag: ${tag}`);
    };

    return (
        <Spin spinning={loading}>
        <div style={{ padding: 10 }}>
            {/* <Row style={{ padding: 10 }}>
                <Col span={24} style={{ wordWrap: 'break-word', marginTop: 5, paddingLeft: 5, textAlign: 'left', lineHeight: '1.5' }}>
                    {tags_keys.map((tag, index) => {
                        const isSelected = tag === selectedTag;
                        return (
                            <div
                                key={index}
                                style={{
                                    display: 'inline-block',
                                    marginRight: 10,
                                    marginBottom: 5,
                                    backgroundColor:isSelected ? theme_blue : '#F0F0F0',
                                    padding: 5,
                                    paddingLeft: 10,
                                    paddingRight: 10,
                                    borderRadius: 5,
                                    color: isSelected ? 'white' : 'black',
                                    cursor: 'pointer',
                                }}
                                onClick={() => handleTagClick(tag)}
                            >
                                {tags_dict[tag]}
                            </div>
                        );
                    })}
                </Col>
            </Row>
            <Search placeholder="搜索应用..." allowClear onChange={onSearch} style={{ width: 300, padding: 10}} /> */}
            <Row gutter={16} style={{marginTop: 20}}>
                {bot_list_tags_filtered.map((bot: Bot, index:any) => {
                    return (
                        <Col className="gutter-row" span={6} key={index}>
                            <div style={{
                                background: '#F0F0F0', 
                                padding: '8px 0',
                                marginBottom: 20,
                                borderRadius: 2,
                                color: 'black',
                                height: 100,
                                cursor: 'pointer',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.background = theme_blue;
                                e.currentTarget.style.color = 'white';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#F0F0F0';
                                e.currentTarget.style.color = 'black';
                            }}
                            onClick={() => onHandleSelectBot(bot)}
                            >
                                <div style={{display: 'flex', alignItems: 'center', marginTop: 0, marginBottom: 0, height: 20, textAlign: 'left'}}>
                                    <ImageComponentPublic 
                                        src={get_application_icon_src(bot)} 
                                        style={{ 
                                            width: '40px',
                                            marginRight: '5px', 
                                            marginLeft: '8px', 
                                            alignSelf: 'flex-start',
                                            borderRadius: '23%',
                                        }} 
                                    />
                                    <div style={{paddingTop: 20, paddingLeft:3 }}><b>{bot.nickname}</b></div>
                                </div>
                                <div style={{textAlign: 'left', fontSize: 12, paddingLeft: 8, paddingRight: 8, paddingTop: 28, height: 30, lineHeight: 1.5}}>
                                    <Tooltip color='cyan' title={bot && bot.description.length > 30 ? bot.description : ''}>
							            <span>{cut_string(bot.description, 30)}</span>
						            </Tooltip>
                                </div>
                            </div>
                        </Col>
                    );
                })}
            </Row>
        </div>
        </Spin>
    );
};