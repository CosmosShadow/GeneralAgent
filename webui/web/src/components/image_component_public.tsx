import React, { useEffect, useState } from 'react';

interface Props {
  src: string;
  style: Object;
}

const ImageComponentPublic: React.FC<Props> = (props) => {
  return (
    <img src={props.src} style={props.style}/>
  );
}
export default ImageComponentPublic;
