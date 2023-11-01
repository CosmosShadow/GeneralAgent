import React from 'react';
import { apiDownloadURL } from './api';

interface Props {
	file_path: string;
	// 可选的title
	title?: any; 
}

// const FileDownloadCompoent: React.FC<Props> = (props) => {
// 	const handleClick = async () => {
// 		// const real_url = await apiDownloadURL(props.file_path);
// 		const real_url = props.file_path
// 		console.log(real_url);
// 		const link = document.createElement('a');
// 		link.href = real_url;
// 		link.setAttribute('download', props.file_path);
// 		document.body.appendChild(link);
// 		link.click();
// 		// 删除掉link
// 		document.body.removeChild(link);
// 	}

// 	const fileName = props.title || props.file_path.substring(props.file_path.lastIndexOf('/') + 1);
// 	// const fileName: string = props.file_path.substring(props.file_path.lastIndexOf('/') + 1);

// 	return (
// 		<a onClick={handleClick} title='点击下载'>{fileName}</a>
// 	);
// }

const FileDownloadCompoent: React.FC<Props> = (props) => {
	const handleClick = async () => {
	  try {
		// const real_url = await apiDownloadURL(props.file_path);
		const real_url = props.file_path;
		console.log(real_url);
		
		const response = await fetch(real_url, {
		  method: 'GET',
		  headers: {
			'Content-Type': 'application/octet-stream', // Set the content type to force download
		  },
		});
		
		const blob = await response.blob(); // Create a Blob object from the response data
		
		const link = document.createElement('a');
		link.href = URL.createObjectURL(blob); // Set the link's href to the Blob object URL
		// link.setAttribute('download', props.file_path);
		link.setAttribute('download', props.file_path.substring(props.file_path.lastIndexOf('/') + 1)); // Set the download attribute to the desired file name
		document.body.appendChild(link);
		link.click();
		
		// Clean up
		document.body.removeChild(link);
		URL.revokeObjectURL(link.href);
	  } catch (error) {
		console.error('Error downloading file:', error);
	  }
	};
  
	const fileName = props.title || props.file_path.substring(props.file_path.lastIndexOf('/') + 1);
  
	return (
	  <a onClick={handleClick} title='点击下载'>{fileName}</a>
	);
  };

export default FileDownloadCompoent;
