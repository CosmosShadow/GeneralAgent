import React, { useCallback, useEffect, useRef, useState } from "react";
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
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleSelectFile(e: React.ChangeEvent<HTMLInputElement>) {
    const fileList = e.target.files;
    if (fileList && fileList.length > 0) {
      setFiles(Array.from(fileList));
      setIsModalVisible(true);
      e.target.value = '';
    }
  }

  async function handleModalOk() {
    try {
      for (let i = 0; i < files.length; i++) {
        let file_path = await apiUploadFile(props.bot_id, props.chat_id, files[i]);
        notification.success({ message: `文件 ${files[i].name} 上传成功` });
        props.onUploadSuccess(file_path);
      }
      setIsModalVisible(false);
      setFiles([]);
    } catch (err) {
      // 处理上传失败的逻辑
      notification.error({ message: '上传失败' });
    }
  }

  function handleModalCancel() {
    setIsModalVisible(false);
    setFiles([]);
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        onChange={handleSelectFile}
        accept="text/plain;charset=utf-8"
        multiple
      />
      <Button onClick={handleButtonClick}>{props.title ? props.title : <UploadOutlined />}</Button>
      <Modal title="上传文件" open={isModalVisible} onOk={handleModalOk} onCancel={handleModalCancel}>
        {files.map((file, index) => (
          <div key={index}>{file.name}</div>
        ))}
      </Modal>
    </>
  );
}

// export function withChatBotId<P extends Props>(Component: React.ComponentType<P>, chat_id: string, bot_id: string) {
//   return function WrappedComponent(props: Omit<P, 'chat_id' | 'bot_id'>) {
//     return <Component {...props as P} chat_id={chat_id} bot_id={bot_id} />;
//   };
// }

interface NewProps {
  title?: string;
  onUploadSuccess: (file_path: string) => void;
}

export const withChatAndBotId = (bot_id: string, chat_id: string) => {
  return (Component: React.ComponentType<Props>) => {
    return (props: NewProps) => <Component {...props} chat_id={chat_id} bot_id={bot_id} />;
  };
};

// 使用高阶组件创建新的组件
// const NewFileUploadButton = withChatBotId(FileUploadButton, 'new_chat_id', 'new_bot_id');

// export const NewFileUploadButton = withChatAndBotId('your_chat_id', 'your_bot_id')(FileUploadButton);