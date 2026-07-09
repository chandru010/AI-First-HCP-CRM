import { configureStore } from '@reduxjs/toolkit';
import crmReducer from '../features/crm/crmSlice';

export const store = configureStore({
  reducer: {
    crm: crmReducer
  }
});
