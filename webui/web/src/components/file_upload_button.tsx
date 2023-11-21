import React, { useState } from "react";
import { Button, Modal, notification} from "antd";
import { apiUploadFile } from "./api"; // 假设这个文件存放apiUploadFile函数
import {
  UploadOutlined,
} from '@ant-design/icons';

interface Props {
  chat_id: string;
  bot_id: string;
  onUploadSuccess: (file_path: string) => void;
  title?: string;
}


export function FileUploadButton(props: Props) {
  // 定义用于显示modal的state以及文件的state
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [file, setFile] = useState(null);

  // 处理选择文件的函数
  function handleSelectFile(e:any) {
    // console.log('handleSelectFile called')
    const fileList = e.target.files;
    if (fileList.length > 0) {
      // 更新选中的文件
      setFile(fileList[0]);
      // 显示modal
      setIsModalVisible(true);
      // 清空input的值，这样下次选择同一个文件还能触发onChange事件
      // console.log('清空input的值')
      e.target.value = null;
    }
  }

  // 处理modal确定按钮的函数
  async function handleModalOk() {
    // console.log('handleModalOk called')
    try {
      let file_path = await apiUploadFile(props.bot_id, props.chat_id, file as any); // 调用apiUploadFile函数上传文件
      // 处理上传成功的逻辑
      setIsModalVisible(false);
      notification.success({ message: '上传成功' });
      setFile(null);
      props.onUploadSuccess(file_path)
    } catch (err) {
      // 处理上传失败的逻辑
      // ...
    }
  }

  // 处理modal取消按钮的函数
  function handleModalCancel() {
    setIsModalVisible(false);
    setFile(null);
  }

  return (
    <>
      <input type="file" style={{ display: "none" }} onChange={handleSelectFile} accept="text/plain;charset=utf-8"/>
      <Button onClick={() => {
         const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
         if (fileInput) {
            fileInput.click();
         }
      }}>{props.title == null ? <UploadOutlined /> : props.title}</Button>
      <Modal title="上传文件" open={isModalVisible} onOk={handleModalOk} onCancel={handleModalCancel}>
        {file && <p>{(file as any).name}</p>}
      </Modal>
    </>
  );
}

interface NewProps {
  title?: string;
  onUploadSuccess: (file_path: string) => void;
}

export const withChatAndBotId = (bot_id: string, chat_id: string) => {
  return (Component: React.ComponentType<Props>) => {
    return (props: NewProps) => <Component {...props} chat_id={chat_id} bot_id={bot_id} />;
  };
};

// export const NewFileUploadButton = withChatAndBotId('your_chat_id', 'your_bot_id')(FileUploadButton);