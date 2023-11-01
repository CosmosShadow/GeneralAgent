import './App.css';
import {Provider} from 'react-redux'
import {store} from './db/redux'
import ChatPage from './pages/chat_page';
import { WebSocketProvider } from './components/WebSocketProvider';


function App() {
  return (
    <div className="App">
      <Provider store={store}>
        <WebSocketProvider>
          <ChatPage />
        </WebSocketProvider>
      </Provider>
    </div>
  );
}

export default App;
