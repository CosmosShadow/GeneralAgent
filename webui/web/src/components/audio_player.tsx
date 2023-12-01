import React, { useEffect, useRef, useState} from 'react';
import { apiDownloadURL } from './api';
import { Button} from 'antd';
import {
	PlayCircleOutlined,
    PauseCircleOutlined
  } from '@ant-design/icons';

interface Props {
    file: string;
}
const AudioPlayer: React.FC<Props> = (props) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const [audioSrc, setAudioSrc] = useState('');
    const [readyPlay, setReadyPlay] = useState(false); // 输入框的内容

    const handleAudioDataLoad = async () => {
        if (audioSrc == '') {
            // const real_url = await apiDownloadURL(props.file);
            const real_url = props.file
            setAudioSrc(real_url)
        }
    }

    const handlePlay = () => {
        if (audioRef.current) {
            if (!readyPlay) {
                audioRef.current.load();
                audioRef.current.play();
                setReadyPlay(true);
            } else {
                audioRef.current.pause();
                audioRef.current.currentTime = 0;
                setReadyPlay(false);
            }
            // setReadyPlay(true);
            // audioRef.current.play();
        }
    }

    useEffect(() => {
        handleAudioDataLoad();
    }, []);

    return (
        <>
            {/* <audio ref={audioRef} src={audioSrc} controls/> */}
            <audio ref={audioRef} src={audioSrc}/>
            <Button type='link' onClick={handlePlay} title='点击播放'>{readyPlay ? <PauseCircleOutlined /> : <PlayCircleOutlined />}</Button>
        </>
    );
}

export default AudioPlayer;


// 在这个版本中，使用 handleAudioDataLoad 作为 useEffect 的回调，保证在组件渲染时加载音频数据。播放操作由 handlePlay 完成，该函数由播放按钮的点击事件触发。因此，我们在点击播放按钮时会呼叫 play() 方法，而不是在 'play' 事件中调用它。