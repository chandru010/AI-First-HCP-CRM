import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './app/store';
import { LogInteractionScreen } from './features/crm/LogInteractionScreen';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <LogInteractionScreen />
    </Provider>
  </React.StrictMode>
);
