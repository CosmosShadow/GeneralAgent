// const React = (window as any).React;
// const antd = (window as any).antd;

import React from 'react';
import * as antd from 'antd';

const [Form, DatePicker, Button] = [antd.Form, antd.DatePicker, antd.Button];

const Lib06f4 = ({send_data}: {send_data: (data:any)=>void}) => {
  const onFinish = (values: any) => {
    send_data(values);
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