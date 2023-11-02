import React, { useEffect, FC, useState} from 'react';
import {Bot, theme_blue} from '../components/interface'
import { Modal, Button, Divider, Select} from 'antd';
import {get_system_file} from './api'
import DynamicUI from './dynamic_ui';

// 
export default function PersonalSetting ({ onHandleSelectBot }: { onHandleSelectBot: (bot: Bot) => void }) {
  const handleChange = (value: string) => {
    console.log(`selected ${value}`);
  };

  return (<div style={{padding: 20}}>正在开发 | Comming soon </div>);

  return (
      <div style={{ padding: 10, textAlign: 'left'}}>
          {/* <div style={{height: 20}}></div> */}
          {/* <Divider orientation="left" plain><b>Setting</b></Divider> */}
          <div>
          Language: &nbsp;<Select
            defaultValue="en"
            style={{ width: 120 }}
            onChange={handleChange}
            options={[
              {
                value: 'en',
                label: 'English',
              },
              {
                value: 'zh',
                label: '中文',
              }
            ]}
          />
          </div>
          <br/>
          <div>
          LLM: &nbsp;<Select
            defaultValue="gpt3.5"
            style={{ width: 120 }}
            onChange={handleChange}
            options={[
              {
                value: 'gpt3.5',
                label: 'GPT3.5',
              },
              {
                value: 'gpt4',
                label: 'GPT4',
              },
              {
                value: 'llama2',
                label: 'LLama2',
              },
              {
                value: '文心一言',
                label: '文心一言',
              },
              {
                value: '通义千问',
                label: '通义千问',
              }
            ]}
          />
          </div>
      </div>
  );
};