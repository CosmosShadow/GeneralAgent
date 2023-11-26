const React = (window as any).React;
const antd = (window as any).antd;

const [Form, Input, Button] = [antd.Form, antd.Input, antd.Button];

const LibTest = ({save_data}: {save_data: (data:any)=>void}) => {
  const onFinish = (values: any) => {
    save_data(values);
    antd.Modal.success({
      title: 'Success',
      content: 'Data saved successfully',
    });
  };

  return (
    <Form onFinish={onFinish}>
      <Form.Item
        label="Name"
        name="name"
        rules={[{ required: true, message: 'Please input your name!' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="Address"
        name="address"
        rules={[{ required: true, message: 'Please input your address!' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="Phone Number"
        name="phone"
        rules={[{ required: true, message: 'Please input your phone number!' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
}

export default LibTest;