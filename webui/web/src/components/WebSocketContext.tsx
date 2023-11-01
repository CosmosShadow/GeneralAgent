import React from 'react';

export const WebSocketContext = React.createContext<{
  sendMessage: (message: string) => void;
  subscribe: (messageHandler: (message: string) => void) => void;
}>({
  sendMessage: () => {},
  subscribe: () => {},
});