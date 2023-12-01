import React, { useEffect, useRef, useState, PropsWithChildren } from 'react';
import { WebSocketContext } from './WebSocketContext';
import {WS_HOST} from './api'

interface Props {}

export const WebSocketProvider: React.FC<PropsWithChildren<Props>> = ({ children }) => {
  const socketRef = useRef<WebSocket | null>(null);
  const [shouldReconnect, setShouldReconnect] = useState(true);
  let reconnectTimerRef: any = null;

  const connectWebSocket = () => {
    const socket = new WebSocket(WS_HOST + '/ws/user/');
    console.log('WebSocket连接OK');
    socketRef.current = socket;
    socket.onclose = () => {
			console.log('WebSocket连接已断开');
			if (shouldReconnect) {
				// 随机的3~5秒后自动重连
				const random = (Math.random() * (5 - 3) + 3) * 1000;
				reconnectTimerRef = setTimeout(() => {
					connectWebSocket();
				}, random);
			}
		};
  };

  useEffect(() => {
    connectWebSocket()
    return () => {
      setShouldReconnect(false); // 取消重连标志
      socketRef.current && socketRef.current.close();
      if (reconnectTimerRef) {
				clearTimeout(reconnectTimerRef); // 取消延迟计时器
			}
    };
  }, []);

  // websocket 心跳
	useEffect(() => {
		const timer = setInterval(() => {
			if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        console.log('ping')
				socketRef.current.send('ping');
			}
		}, 10000);
		return () => clearInterval(timer);
	}, []);

  const sendMessage = (message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    }
  };

  const subscribe = (messageHandler: (message: string) => void) => {
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        // console.log(event);
        if (event.data == 'pong') {
          console.log('pong')
        } else {
          messageHandler(event.data);
        }
      };
    }
  };

  return (
    <WebSocketContext.Provider value={{ sendMessage, subscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
};