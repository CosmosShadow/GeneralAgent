const React = (window as any).React;
const antd = (window as any).antd;

interface Props {
  save_data: (user_data:any)=>void,
  FileUploadConponent: (props: {onUploadSuccess: (file_path: string) => void, title?: string}) => React.ReactElement
}

const Lib64d4 = (props: Props) => {
  const [filePath, setFilePath] = React.useState('');

  const handleUploadSuccess = (file_path: string) => {
    setFilePath(file_path);
  };

  const handleCommit = () => {
    const all_data_should_save = {
      filePath
    };
    props.save_data(all_data_should_save);
  };

  return (
    <>
      <props.FileUploadConponent onUploadSuccess={handleUploadSuccess} title='' />
      <div>{filePath}</div>
      <antd.Select defaultValue="Chinese">
        <antd.Select.Option value="Chinese">Chinese</antd.Select.Option>
        <antd.Select.Option value="Japanese">Japanese</antd.Select.Option>
        <antd.Select.Option value="English">English</antd.Select.Option>
      </antd.Select>
      <antd.Button type="primary" onClick={handleCommit}>Commit</antd.Button>
    </>
  );
};

export default Lib64d4;