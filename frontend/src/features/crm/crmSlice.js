import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchCrmData = createAsyncThunk('crm/fetch', async () => {
  const [hcps, interactions] = await Promise.all([
    api.get('/hcps'),
    api.get('/interactions')
  ]);
  return { hcps: hcps.data, interactions: interactions.data };
});

export const createInteraction = createAsyncThunk('crm/createInteraction', async (payload) => {
  const response = await api.post('/interactions', payload);
  return response.data;
});

export const chatWithAgent = createAsyncThunk('crm/chatWithAgent', async (payload) => {
  const response = await api.post('/agent/chat', payload);
  return response.data;
});

export const runToolDemo = createAsyncThunk('crm/runToolDemo', async () => {
  const response = await api.post('/agent/tools/demo');
  return response.data;
});

const crmSlice = createSlice({
  name: 'crm',
  initialState: {
    hcps: [],
    interactions: [],
    chat: [
      {
        role: 'assistant',
        content: 'Ready to log visits, edit records, check compliance, and suggest next actions.'
      }
    ],
    demoResults: [],
    status: 'idle',
    error: ''
  },
  reducers: {
    addUserMessage(state, action) {
      state.chat.push({ role: 'user', content: action.payload });
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCrmData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchCrmData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.hcps = action.payload.hcps;
        state.interactions = action.payload.interactions;
      })
      .addCase(fetchCrmData.rejected, (state, action) => {
        state.status = 'error';
        state.error = action.error.message;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.interactions.unshift(action.payload);
      })
      .addCase(chatWithAgent.fulfilled, (state, action) => {
        state.chat.push({
          role: 'assistant',
          content: action.payload.answer,
          meta: `${action.payload.tool_name} | ${action.payload.intent}`
        });
        if (action.payload.tool_name === 'log_interaction') {
          state.interactions.unshift(action.payload.tool_result.interaction);
        }
      })
      .addCase(runToolDemo.fulfilled, (state, action) => {
        state.demoResults = action.payload.results;
      });
  }
});

export const { addUserMessage } = crmSlice.actions;
export default crmSlice.reducer;
