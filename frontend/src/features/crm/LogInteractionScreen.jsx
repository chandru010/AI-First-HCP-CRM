import React, { useEffect, useMemo, useState } from 'react';
import { Bot, CalendarCheck, CheckCircle2, FileText, PencilLine, Send, Sparkles, Stethoscope } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { Badge } from '../../components/Badge';
import { addUserMessage, chatWithAgent, createInteraction, fetchCrmData, runToolDemo } from './crmSlice';

const today = new Date().toISOString().slice(0, 10);

const emptyForm = {
  hcp_id: '',
  hcp_name: '',
  interaction_date: '',
  interaction_time: '',
  interaction_type: '',
  attendees: '',
  channel: '',
  products_discussed: '',
  topics_discussed: '',
  samples_dropped: '',
  materials_shared: '',
  discussion_outcomes: '',
  sentiment: '',
  notes: '',
  follow_up_date: '',
  follow_up_action: ''
};

const splitList = (value) => value.split(',').map((item) => item.trim()).filter(Boolean);
const joinList = (value) => Array.isArray(value) ? value.join(', ') : value || '';

function findHcpIdByName(hcps, hcpName) {
  if (!hcpName) return '';
  const normalized = hcpName.toLowerCase().replace(/\./g, '').trim();
  const match = hcps.find((hcp) => hcp.name.toLowerCase().replace(/\./g, '').trim() === normalized);
  return match?.id || '';
}

function interactionToDraft(interaction) {
  return {
    hcp_id: interaction.hcp_id || '',
    hcp_name: interaction.hcp_name || '',
    interaction_date: interaction.interaction_date?.slice(0, 10) || today,
    interaction_time: interaction.interaction_date?.slice(11, 16) || '',
    interaction_type: 'Meeting',
    attendees: '',
    channel: interaction.channel || 'In-person',
    products_discussed: joinList(interaction.products_discussed),
    topics_discussed: joinList(interaction.topics_discussed),
    samples_dropped: joinList(interaction.samples_dropped),
    materials_shared: '',
    discussion_outcomes: interaction.summary || '',
    sentiment: interaction.sentiment || '',
    notes: interaction.notes || '',
    follow_up_date: interaction.follow_up_date || '',
    follow_up_action: interaction.follow_up_action || ''
  };
}

export function LogInteractionScreen() {
  const dispatch = useDispatch();
  const { hcps, interactions, chat, demoResults, status, error } = useSelector((state) => state.crm);
  const [form, setForm] = useState(emptyForm);
  const [chatText, setChatText] = useState('');
  const [currentInteractionId, setCurrentInteractionId] = useState(null);
  const [saveState, setSaveState] = useState('');

  useEffect(() => {
    dispatch(fetchCrmData());
  }, [dispatch]);

  const selectedHcp = useMemo(
    () => hcps.find((hcp) => Number(hcp.id) === Number(form.hcp_id)),
    [hcps, form.hcp_id]
  );

  const applyExtractedToForm = (extracted, interaction) => {
    setForm((current) => {
      const next = interaction ? { ...current, ...interactionToDraft(interaction) } : { ...current };
      const hcpName = extracted.hcp_name || next.hcp_name;
      const hcpId = extracted.hcp_id || findHcpIdByName(hcps, hcpName) || next.hcp_id;
      return {
        ...next,
        hcp_id: hcpId,
        hcp_name: hcpName || next.hcp_name,
        interaction_date: extracted.interaction_date || next.interaction_date || today,
        interaction_time: extracted.interaction_time || next.interaction_time,
        interaction_type: extracted.interaction_type || next.interaction_type || 'Meeting',
        attendees: extracted.attendees || next.attendees,
        channel: extracted.channel || next.channel || 'In-person',
        products_discussed: extracted.products_discussed ? joinList(extracted.products_discussed) : next.products_discussed,
        topics_discussed: extracted.topics_discussed ? joinList(extracted.topics_discussed) : next.topics_discussed,
        samples_dropped: extracted.samples_dropped ? joinList(extracted.samples_dropped) : next.samples_dropped,
        materials_shared: extracted.materials_shared ? joinList(extracted.materials_shared) : next.materials_shared,
        discussion_outcomes: extracted.discussion_outcomes || next.discussion_outcomes,
        sentiment: extracted.sentiment || next.sentiment,
        notes: extracted.notes || next.notes,
        follow_up_date: extracted.follow_up_date || next.follow_up_date,
        follow_up_action: extracted.follow_up_action || next.follow_up_action
      };
    });
  };

  const submitChat = async (event) => {
    event.preventDefault();
    if (!chatText.trim()) return;
    const prompt = chatText;
    dispatch(addUserMessage(prompt));
    setChatText('');
    setSaveState('');
    const result = await dispatch(chatWithAgent({
      message: prompt,
      hcp_id: form.hcp_id ? Number(form.hcp_id) : undefined,
      interaction_id: currentInteractionId || undefined
    })).unwrap();
    const interaction = result.tool_result?.interaction;
    if (interaction?.id) {
      setCurrentInteractionId(interaction.id);
    }
    applyExtractedToForm(result.extracted || {}, interaction);
  };

  const saveDraft = async (event) => {
    event.preventDefault();
    if (currentInteractionId) {
      setSaveState(`Interaction #${currentInteractionId} already logged by AI`);
      return;
    }
    const hcpId = form.hcp_id || findHcpIdByName(hcps, form.hcp_name) || hcps[0]?.id;
    if (!hcpId) return;
    const saved = await dispatch(createInteraction({
      hcp_id: Number(hcpId),
      interaction_date: form.interaction_date ? new Date(`${form.interaction_date}T${form.interaction_time || '09:00'}`).toISOString() : undefined,
      channel: form.channel || 'In-person',
      products_discussed: splitList(form.products_discussed),
      topics_discussed: splitList(form.topics_discussed),
      samples_dropped: splitList(form.samples_dropped),
      sentiment: form.sentiment || 'Neutral',
      notes: form.notes || form.discussion_outcomes || 'AI-assisted HCP interaction.',
      follow_up_date: form.follow_up_date,
      follow_up_action: form.follow_up_action
    })).unwrap();
    setCurrentInteractionId(saved.id);
    setSaveState(`Interaction #${saved.id} saved`);
  };

  const hasDraft = Object.values(form).some(Boolean);

  return (
    <main className="screen">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark"><Stethoscope size={22} /></div>
          <div>
            <strong>AI-First HCP CRM</strong>
            <span>LangGraph powered interaction logging</span>
          </div>
        </div>
        <button className="secondary" onClick={() => dispatch(runToolDemo())}>
          <Sparkles size={18} /> Demo all tools
        </button>
      </header>

      {status === 'error' && <div className="error">{error}</div>}

      <section className="split-shell">
        <form className="interaction-form" onSubmit={saveDraft}>
          <div className="panel-title">
            <div>
              <h1>Log HCP Interaction</h1>
              <p>Fields are populated by the AI assistant.</p>
            </div>
            {currentInteractionId ? <Badge tone="positive">Logged #{currentInteractionId}</Badge> : <Badge tone="ai">AI Draft</Badge>}
          </div>

          <section className="form-section">
            <h2>Interaction Details</h2>
            <div className="row two">
              <label className="field">
                <span>HCP Name</span>
                <input readOnly value={form.hcp_name} placeholder="Waiting for assistant..." />
              </label>
              <label className="field">
                <span>Interaction Type</span>
                <input readOnly value={form.interaction_type} placeholder="Meeting" />
              </label>
            </div>

            <div className="row two">
              <label className="field">
                <span>Date</span>
                <input readOnly value={form.interaction_date} placeholder="YYYY-MM-DD" />
              </label>
              <label className="field">
                <span>Time</span>
                <input readOnly value={form.interaction_time} placeholder="09:00 AM" />
              </label>
            </div>

            <label className="field">
              <span>Attendees</span>
              <input readOnly value={form.attendees} placeholder="Enter names of reps/HCPs" />
            </label>
          </section>

          <section className="form-section">
            <h2>Topics Discussed</h2>
            <textarea readOnly value={form.topics_discussed} placeholder="AI extracts discussion topics here." />
          </section>

          <section className="form-section">
            <h2>Materials Shared / Samples Dropped</h2>
            <input readOnly value={form.materials_shared || form.samples_dropped} placeholder="Brochures, samples, clinical evidence" />
          </section>

          <section className="form-section">
            <h2>Discussion Outcomes</h2>
            <textarea readOnly value={form.discussion_outcomes || form.notes} placeholder="AI summarizes outcomes and commitments." />
          </section>

          <div className="row two">
            <label className="field">
              <span>Sentiment</span>
              <input readOnly value={form.sentiment} placeholder="Positive / Neutral / Negative" />
            </label>
            <label className="field">
              <span>Product</span>
              <input readOnly value={form.products_discussed} placeholder="Product X" />
            </label>
          </div>

          {selectedHcp && (
            <div className="hcp-context">
              <FileText size={17} />
              <span>{selectedHcp.specialty} | {selectedHcp.territory} | Segment {selectedHcp.segment}</span>
            </div>
          )}

          <div className="form-actions">
            <button className="primary" type="submit" disabled={!hasDraft}>
              {currentInteractionId ? <CheckCircle2 size={18} /> : <PencilLine size={18} />}
              {currentInteractionId ? 'Logged by AI' : 'Log'}
            </button>
            {saveState && <span>{saveState}</span>}
          </div>
        </form>

        <aside className="assistant-panel">
          <div className="assistant-header">
            <div>
              <h2><Bot size={19} /> AI Assistant</h2>
              <p>Use natural language to fill or correct the form.</p>
            </div>
            <Badge tone="ai">Groq + LangGraph</Badge>
          </div>

          <div className="prompt-examples">
            <button type="button" onClick={() => setChatText('Today I met with Dr. Smith and discussed Product X efficacy. The sentiment was positive and I shared the brochures.')}>
              Log example
            </button>
            <button type="button" onClick={() => setChatText('Sorry, the name was actually Dr. John and the sentiment was negative.')}>
              Edit example
            </button>
          </div>

          <div className="messages">
            {chat.map((message, index) => (
              <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
                <div className="avatar">{message.role === 'assistant' ? <Bot size={17} /> : <Stethoscope size={17} />}</div>
                <div>
                  <p>{message.content}</p>
                  {message.meta && <span>{message.meta}</span>}
                </div>
              </div>
            ))}
          </div>

          <form className="chat-input" onSubmit={submitChat}>
            <input value={chatText} onChange={(event) => setChatText(event.target.value)} placeholder="Type an instruction for the assistant..." />
            <button className="primary icon" type="submit"><Send size={18} /></button>
          </form>
        </aside>
      </section>

      <section className="lower-grid">
        <aside className="tool-panel">
          <h2>LangGraph Tools</h2>
          {demoResults.length === 0 ? (
            <p className="empty">Run the tool demo to show the five-plus LangGraph tools.</p>
          ) : demoResults.map((result, index) => (
            <div className="demo-item" key={`${result.tool}-${index}`}>
              <Badge tone="ai">{result.tool}</Badge>
              <span>{result.message || result.recommendation || result.action || result.error || 'Tool executed successfully'}</span>
            </div>
          ))}
        </aside>

        <aside className="recent-panel">
          <h2>Recent Logs</h2>
          {interactions.slice(0, 3).map((interaction) => (
            <article className="interaction" key={interaction.id}>
              <div className="interaction-head">
                <strong>{interaction.hcp_name}</strong>
                <Badge tone={interaction.sentiment.toLowerCase()}>{interaction.sentiment}</Badge>
              </div>
              <p>{interaction.summary}</p>
              {interaction.follow_up_action && (
                <div className="follow-up"><CalendarCheck size={15} /> {interaction.follow_up_action}</div>
              )}
            </article>
          ))}
        </aside>
      </section>
    </main>
  );
}
