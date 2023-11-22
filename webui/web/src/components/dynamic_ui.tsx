import React from 'react';
import * as antd from 'antd';
import axios from 'axios';

interface Props {
  name: string;
  js_url: string;
  data: any;
  save_data: (data: any) => void;
  FileUploadConponent?: any;
}

const DynamicUI: React.FC<Props> = (props) => {
  const scriptSrc = props.js_url;
  const [scriptLoaded, setScriptLoaded] = React.useState(false);

  React.useEffect(() => {
    (window as any).React = React;
    (window as any).antd = antd;
    loadRemoteComponent();
    return () => {
      unloadRemoteComponent();
    };
  }, []);

  const loadRemoteComponent = () => {
    axios.get(scriptSrc)
      .then(response => {
        const scriptCode = response.data;
        eval(scriptCode);
        // console.log((window as any)[props.name]);
        setScriptLoaded(true);
      })
      .catch(error => {
        console.error('Failed to load script:', error);
      });
  }

  const unloadRemoteComponent = () => {
    delete (window as any)[props.name];
    setScriptLoaded(false);
  }

  // console.log((window as any)[props.name]);

  const Component = scriptLoaded && (window as any)[props.name] && (window as any)[props.name].default;

  return (
    <div>
      {/* {Component && <Component data={props.data} save_data={props.save_data}/>} */}
      {Component && <Component save_data={props.save_data} FileUploadConponent={props.FileUploadConponent}/>}
    </div>
  );
}

export default DynamicUI;