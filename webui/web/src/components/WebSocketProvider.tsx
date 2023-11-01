import React, { useEffect, useState, PropsWithChildren } from 'react';
import { WebSocketContext } from './WebSocketContext';
import {WS_HOST} from './api'

interface Props {}

export const WebSocketProvider: React.FC<PropsWithChildren<Props>> = ({ children }) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [shouldReconnect, setShouldReconnect] = useState(true);
  let reconnectTimerRef: any = null;

  const connectWebSocket = () => {
    const socket = new WebSocket(WS_HOST + '/ws/user/');
    setSocket(socket);
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
      socket && socket.close();
      if (reconnectTimerRef) {
				clearTimeout(reconnectTimerRef); // 取消延迟计时器
			}
    };
  }, []);

  // websocket 心跳
	useEffect(() => {
		const timer = setInterval(() => {
			if (socket && socket.readyState === WebSocket.OPEN) {
        console.log('ping')
				socket.send('ping');
			}
		}, 10000);
		return () => clearInterval(timer);
	}, []);

  const sendMessage = (message: string) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  const subscribe = (messageHandler: (message: string) => void) => {
    if (socket) {
      socket.onmessage = (event) => {
        if (event.data != 'pong') {
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