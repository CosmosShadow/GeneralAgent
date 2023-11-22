// const React = (window as any).React;
// const antd = (window as any).antd;


import React from 'react';
import * as antd from 'antd';

interface Props {
  save_data: (data:any)=>void,
  FileUploadConponent: (props: {onUploadSuccess: (file_path: string) => void, title?: string}) => React.ReactElement
}

const [Form, DatePicker, Button] = [antd.Form, antd.DatePicker, antd.Button];

const Lib06f4 = (props: Props) => {
  const [file_path, set_file_path] = React.useState('' as string)

  const onFinish = (values: any) => {
    values['file_path'] = file_path
    props.save_data(values);
  };

  const handleUploadSuccess = (file_path: string) => {
    console.log('handleUploadSuccess called')
    console.log(file_path)
    set_file_path(file_path)
  }

  return (
    <div style={{}}>
      <props.FileUploadConponent onUploadSuccess={handleUploadSuccess} title='上传文件'/>
      <div style={{padding: 10}}>file_path: {file_path}</div>
      <Form onFinish={onFinish}>
        <Form.Item name="date" rules={[{ required: true, message: 'Please select a date' }]}>
          <DatePicker />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Lib06f4;