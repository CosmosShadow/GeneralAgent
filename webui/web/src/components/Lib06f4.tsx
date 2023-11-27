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
  const [file1Path, setFile1Path] = React.useState("");
  const [file2Path, setFile2Path] = React.useState("");
  const [outputPath, setOutputPath] = React.useState("");

  const handleFile1UploadSuccess = (path: string) => {
    setFile1Path(path);
  };

  const handleFile2UploadSuccess = (path: string) => {
    setFile2Path(path);
  };

  const handleCommit = () => {
    const allDataShouldSave = {
      file1Path,
      file2Path,
      outputPath
    };
    props.save_data(allDataShouldSave);
  };

  return (
    <>
      <props.FileUploadConponent
        onUploadSuccess={handleFile1UploadSuccess}
        title="Select File 1"
      />
      <props.FileUploadConponent
        onUploadSuccess={handleFile2UploadSuccess}
        title="Select File 2"
      />
      <antd.Input
        value={outputPath}
        onChange={(e: any) => setOutputPath(e.target.value)}
        placeholder="Output File Path"
      />
      <antd.Button type="primary" onClick={handleCommit}>
        Save
      </antd.Button>
    </>
  );
};

export default Lib06f4;