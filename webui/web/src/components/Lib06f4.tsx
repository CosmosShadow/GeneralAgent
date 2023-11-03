// const React = (window as any).React;

import React from 'react';
import * as antd from 'antd';

const [Form, DatePicker, Button] = [antd.Form, antd.DatePicker, antd.Button];

interface Props {
  data: any;
  send_data: (data: any) => void;
}

const Lib06f4 = (props:Props) => {
  const onFinish = (values: any) => {
    // console.log(send_data);
    props.send_data(values);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
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