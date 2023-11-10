import React from 'react';
import { Image } from 'antd';
import FileDownloadCompoent from './file_download'
import {
	CloudDownloadOutlined,
  } from '@ant-design/icons';

interface Props {
  image_url: string;
}

const ImageComponent: React.FC<Props> = (props) => {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'flex-end', paddingTop: 8}}>
      <div>
        <Image src={props.image_url} alt="loading" style={{ height: 300, width: 'auto', maxWidth: '100%' }} />
      </div>
      <div style={{paddingLeft: 10}}>
        <FileDownloadCompoent title={<CloudDownloadOutlined />} file_path={props.image_url} />
      </div>
    </div>
  );
}

export default ImageComponent;
