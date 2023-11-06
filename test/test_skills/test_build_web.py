

code = """
const React = (window as any).React;
const antd = (window as any).antd;

const MyLibrary = () => {
    const { Form, Input, Button, Modal } = antd;
    const [visible, setVisible] = React.useState(false);
    const [summary, setSummary] = React.useState('');
  
    const onFinish = (values: any) => {
      const { name, address, phone } = values;
      const summary = `姓名: ${name}\n家庭住址: ${address}\n手机号: ${phone}`;
      setSummary(summary);
      setVisible(true);
    };
  
    const handleOk = () => {
      setVisible(false);
    };
  
    const handleCancel = () => {
      setVisible(false);
    };
  
    return (
      <div>
        <Form onFinish={onFinish}>
          <Form.Item
            label="姓名"
            name="name"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input />
          </Form.Item>
  
          <Form.Item
            label="家庭住址"
            name="address"
            rules={[{ required: true, message: '请输入家庭住址' }]}
          >
            <Input />
          </Form.Item>
  
          <Form.Item
            label="手机号"
            name="phone"
            rules={[{ required: true, message: '请输入手机号' }]}
          >
            <Input />
          </Form.Item>
  
          <Form.Item>
            <Button type="primary" htmlType="submit">
              提交
            </Button>
          </Form.Item>
        </Form>
  
        <Modal
          title="提交内容概要"
          visible={visible}
          onOk={handleOk}
          onCancel={handleCancel}
        >
          <p>{summary}</p>
        </Modal>
      </div>
    );
  };

export default MyLibrary;
"""

def test_compile_tsx():
    from GeneralAgent import skills
    target_dir = './data/ui/'
    success = skills.compile_tsx(code, target_dir)
    assert success

def test_create_ui():
    from GeneralAgent import skills
    task = "用户输入姓名、家庭住址、手机号的表单，并且点击提交的时候，弹窗显示"
    lib_name = 'LibTest'
    js_path, lib_name = skills.create_ui(task, lib_name=lib_name)
    # 验证js文件存在
    import os
    assert os.path.exists(js_path)
    assert lib_name in js_path

if __name__ == '__main__':
    # test_compile_tsx()
    test_create_ui()