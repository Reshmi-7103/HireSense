import { useState, useEffect, useRef } from 'react';
import { MessageCircle, User, Mic, MicOff, Plus, Trash2, ChevronLeft, Clock, VolumeX } from 'lucide-react';
import Navbar from "../components/NavbarLogin";

/* ─── Design Tokens ─── */
const T = {
  bg:          'linear-gradient(135deg, #020810 0%, #060f1e 50%, #080d1a 100%)',
  sidebar:     'rgba(4, 11, 24, 0.98)',
  sidebarBdr:  'rgba(99, 255, 218, 0.1)',
  border:      'rgba(99, 255, 218, 0.15)',
  accent:      '#64ffda',
  accentDim:   'rgba(100, 255, 218, 0.08)',
  accentMid:   'rgba(100, 255, 218, 0.16)',
  accentGlow:  'rgba(100, 255, 218, 0.35)',
  text:        '#dce9f5',
  muted:       '#7899bb',
  subtle:      '#a8c0d6',
  userBubble:  'linear-gradient(145deg, #0d3a6e 0%, #0f5499 100%)',
  aiBubble:    'rgba(8, 18, 36, 0.9)',
};

const globalStyle = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body, #root { height: 100%; }
  body { background: ${T.bg}; color: ${T.text}; font-family: 'DM Sans', sans-serif; overflow: hidden; }
  ::-webkit-scrollbar { width: 3px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(100,255,218,0.2); border-radius: 10px; }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  @keyframes pulseRing {
    0%   { box-shadow: 0 0 0 0 rgba(100,255,218,0.55); }
    70%  { box-shadow: 0 0 0 18px rgba(100,255,218,0); }
    100% { box-shadow: 0 0 0 0 rgba(100,255,218,0); }
  }
  @keyframes dotPulse {
    from { opacity: 0.2; transform: scale(0.75); }
    to   { opacity: 1;   transform: scale(1.25); }
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
  }
`;

/* ════════════════════════════════════════
   MAIN COMPONENT
════════════════════════════════════════ */
export default function Interview() {
  const [interviews, setInterviews]             = useState([]);
  const [currentInterview, setCurrentInterview] = useState(null);
  const [messages, setMessages]                 = useState([]);
  const [isLoading, setIsLoading]               = useState(false);
  const [interviewType, setInterviewType]       = useState(null);
  const [isListening, setIsListening]           = useState(false);
  const [isSpeaking, setIsSpeaking]             = useState(false);
  const [liveTranscript, setLiveTranscript]     = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [deleteConfirm, setDeleteConfirm]       = useState(null);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const synthRef       = useRef(null);
  // These refs keep track of state inside recognition callbacks
  const accumulatedRef    = useRef(''); // full confirmed text so far
  const isListeningRef    = useRef(false); // true = user wants mic ON

  /* ─────────────────────────────────────
     SPEECH RECOGNITION — continuous mode
     User presses mic ON  → starts capturing
     User presses mic OFF → stops & sends
  ───────────────────────────────────── */
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;

    const rec = new SR();
    rec.continuous      = true;   // ← keep alive until we manually stop
    rec.interimResults  = true;
    rec.lang            = 'en-US';
    rec.maxAlternatives = 1;

    rec.onstart = () => {
      isListeningRef.current = true;
      setIsListening(true);
      accumulatedRef.current = '';
      setLiveTranscript('');
    };

    rec.onresult = (e) => {
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) {
          accumulatedRef.current += t + ' ';
        } else {
          interim += t;
        }
      }
      // Show everything the user has said so far
      setLiveTranscript((accumulatedRef.current + interim).trim());
    };

    rec.onerror = (e) => {
      if (e.error === 'not-allowed') {
        alert('Microphone access denied. Please allow microphone in browser settings.');
        isListeningRef.current = false;
        setIsListening(false);
        return;
      }
      // For other errors (network, aborted), restart if still supposed to be on
      if (isListeningRef.current) {
        try { rec.start(); } catch {}
      }
    };

    rec.onend = () => {
      // Browser stopped internally — restart if user hasn't pressed stop
      if (isListeningRef.current) {
        try { rec.start(); } catch {}
      }
    };

    recognitionRef.current = rec;
    synthRef.current = window.speechSynthesis;

    return () => {
      isListeningRef.current = false;
      try { rec.stop(); } catch {}
      synthRef.current?.cancel();
    };
  }, []);

  useEffect(() => { loadInterviews(); }, []);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  /* ── TTS ── */
  const speak = (text) => {
    if (!synthRef.current || !text?.trim()) return;
    synthRef.current.cancel();
    setTimeout(() => {
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 0.9; u.pitch = 1; u.volume = 1; u.lang = 'en-US';
      u.onstart = () => setIsSpeaking(true);
      u.onend   = () => setIsSpeaking(false);
      u.onerror = () => setIsSpeaking(false);
      try { synthRef.current.speak(u); } catch { setIsSpeaking(false); }
    }, 100);
  };
  const stopSpeaking = () => { synthRef.current?.cancel(); setIsSpeaking(false); };

  /* ── START mic ── */
  const startListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition not supported. Please use Chrome or Edge.');
      return;
    }
    stopSpeaking();
    accumulatedRef.current = '';
    setLiveTranscript('');
    isListeningRef.current = true;
    try { recognitionRef.current.start(); } catch {}
    setIsListening(true);
  };

  /* ── STOP mic → send accumulated text ── */
  const stopListeningAndSend = () => {
    isListeningRef.current = false;
    setIsListening(false);
    try { recognitionRef.current?.stop(); } catch {}

    const finalText = accumulatedRef.current.trim();
    accumulatedRef.current = '';
    setLiveTranscript('');

    if (finalText) {
      handleVoiceInput(finalText);
    }
  };

  /* ── Toggle ── */
  const toggleListening = () => {
    if (isLoading) return;
    if (!currentInterview) {
      startNewInterview('technical');
      setTimeout(startListening, 600);
      return;
    }
    isListening ? stopListeningAndSend() : startListening();
  };

  /* ── Storage ── */
  const loadInterviews = () => {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('interview:'));
    const data = keys
      .map(k => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } })
      .filter(Boolean);
    setInterviews(data.sort((a, b) => b.timestamp - a.timestamp));
  };

  /* ── AI API call ── */
  const handleVoiceInput = async (voiceTranscript) => {
    if (!voiceTranscript.trim()) return;

    let interview = currentInterview;
    if (!interview) {
      const keys = Object.keys(localStorage).filter(k => k.startsWith('interview:')).sort().reverse();
      if (keys.length) {
        interview = JSON.parse(localStorage.getItem(keys[0]));
        setCurrentInterview(interview);
        setInterviewType(interview.type);
        setMessages(interview.messages || []);
      }
    }
    if (!interview) return;

    const userMessage     = { role: 'user', content: voiceTranscript };
    const updatedMessages = [...(interview.messages || []), userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const sys = interview.type === 'technical'
        ? "You are an experienced technical interviewer. Ask relevant technical questions. Keep responses concise."
        : "You are an experienced HR interviewer. Keep responses friendly and concise.";

      const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${import.meta.env.VITE_GROQ_API_KEY}`
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: [{ role: 'system', content: sys }, ...updatedMessages],
          temperature: 0.7,
          max_tokens: 500
        })
      });

      const data  = await res.json();
      const aiMsg = { role: 'assistant', content: data.choices[0].message.content };
      const final = [...updatedMessages, aiMsg];
      setMessages(final);
      setTimeout(() => speak(aiMsg.content), 400);

      const updated = { ...interview, messages: final, timestamp: Date.now() };
      setCurrentInterview(updated);
      localStorage.setItem(`interview:${updated.id}`, JSON.stringify(updated));
      loadInterviews();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  /* ── Interview Actions ── */
  const startNewInterview = (type) => {
    stopSpeaking();
    const nw = {
      id: Date.now().toString(), type, timestamp: Date.now(),
      title: `${type === 'technical' ? 'Technical' : 'HR'} Interview`,
      messages: []
    };
    const init = {
      role: 'assistant',
      content: type === 'technical'
        ? "Hello! I'm your AI technical interviewer. Let's start — can you tell me about your technical background and experience?"
        : "Hello! I'm your AI HR interviewer. Let's begin — can you tell me about yourself and why you're interested in this position?"
    };
    nw.messages = [init];
    setCurrentInterview(nw);
    setMessages([init]);
    setInterviewType(type);
    setTimeout(() => speak(init.content), 500);
    localStorage.setItem(`interview:${nw.id}`, JSON.stringify(nw));
    loadInterviews();
  };

  const loadInterview = (iv) => {
    stopSpeaking();
    setCurrentInterview(iv);
    setMessages(iv.messages);
    setInterviewType(iv.type);
  };

  const deleteInterview = (id) => {
    localStorage.removeItem(`interview:${id}`);
    setDeleteConfirm(null);
    loadInterviews();
    if (currentInterview?.id === id) {
      stopSpeaking();
      setCurrentInterview(null); setMessages([]); setInterviewType(null);
    }
  };

  const goBack = () => {
    // Make sure mic is fully stopped
    isListeningRef.current = false;
    setIsListening(false);
    try { recognitionRef.current?.stop(); } catch {}
    accumulatedRef.current = '';
    setLiveTranscript('');
    stopSpeaking();
    setIsLoading(false);
    setCurrentInterview(null); setMessages([]); setInterviewType(null);
  };

  /* ── Helpers ── */
  const formatDate = (ts) => {
    const d = new Date(ts);
    const today     = new Date();
    const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
    if (d.toDateString() === today.toDateString())
      return `Today, ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    if (d.toDateString() === yesterday.toDateString())
      return `Yesterday, ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    return d.toLocaleDateString([], { day: 'numeric', month: 'short' }) +
           ', ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const msgPreview = (iv) => {
    const last = iv.messages?.[iv.messages.length - 1];
    if (!last) return 'No messages yet';
    return last.content.length > 52 ? last.content.slice(0, 52) + '…' : last.content;
  };

  /* ════════════════════
     RENDER
  ════════════════════ */
  return (
    <>
      <style>{globalStyle}</style>

      <div style={{
        display: 'flex', flexDirection: 'column',
        height: '100vh', width: '100vw',
        background: T.bg, overflow: 'hidden',
        fontFamily: "'DM Sans', sans-serif", color: T.text,
      }}>
        {/* ── Top Navbar ── */}
        <Navbar />

        {/* ── Sidebar + Main row ── */}
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden', minHeight: 0 }}>

          {/* ══════════ LEFT SIDEBAR ══════════ */}
          <aside style={{
            width: sidebarCollapsed ? 64 : 268,
            minWidth: sidebarCollapsed ? 64 : 268,
            height: '100%',
            background: T.sidebar,
            borderRight: `1px solid ${T.sidebarBdr}`,
            display: 'flex', flexDirection: 'column',
            transition: 'width .3s cubic-bezier(.4,0,.2,1), min-width .3s cubic-bezier(.4,0,.2,1)',
            overflow: 'hidden', position: 'relative', zIndex: 10, flexShrink: 0,
          }}>

            {/* Sidebar Header */}
            <div style={{
              padding: sidebarCollapsed ? '20px 0' : '22px 18px 18px',
              borderBottom: `1px solid ${T.sidebarBdr}`,
              display: 'flex', alignItems: 'center',
              justifyContent: sidebarCollapsed ? 'center' : 'space-between',
              gap: 10, flexShrink: 0,
            }}>
              {!sidebarCollapsed && (
                <div style={{ animation: 'fadeIn .25s ease' }}>
                  <div style={{
                    fontFamily: "'Syne', sans-serif", fontWeight: 800,
                    fontSize: 17, color: T.accent, letterSpacing: 1, lineHeight: 1,
                  }}>HireSense</div>
                  <div style={{ fontSize: 10, color: T.muted, letterSpacing: 2, textTransform: 'uppercase', marginTop: 3 }}>
                    AI Interviewer
                  </div>
                </div>
              )}
              <button
                onClick={() => setSidebarCollapsed(p => !p)}
                title={sidebarCollapsed ? 'Expand' : 'Collapse'}
                style={{
                  background: T.accentDim, border: `1px solid ${T.border}`,
                  color: T.accent, borderRadius: 8, width: 32, height: 32,
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0, transition: 'all .2s',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = T.accentMid; e.currentTarget.style.borderColor = T.accent; }}
                onMouseLeave={e => { e.currentTarget.style.background = T.accentDim; e.currentTarget.style.borderColor = T.border; }}
              >
                <ChevronLeft size={15} style={{ transform: sidebarCollapsed ? 'rotate(180deg)' : 'none', transition: 'transform .3s' }} />
              </button>
            </div>

            {/* Back button — only when inside an interview */}
            {currentInterview && (
              <div style={{
                padding: sidebarCollapsed ? '12px 8px' : '12px 14px',
                borderBottom: `1px solid ${T.sidebarBdr}`,
                flexShrink: 0, animation: 'slideIn .25s ease',
              }}>
                <SidebarBtn
                  icon={<ChevronLeft size={16} />}
                  label="Back to Home"
                  collapsed={sidebarCollapsed}
                  onClick={goBack}
                  title="Back to Home"
                />
              </div>
            )}

            {/* New Interview */}
            <div style={{
              padding: sidebarCollapsed ? '12px 8px' : '12px 14px',
              borderBottom: `1px solid ${T.sidebarBdr}`, flexShrink: 0,
            }}>
              {sidebarCollapsed ? (
                <button
                  title="New Interview"
                  onClick={() => { setSidebarCollapsed(false); goBack(); }}
                  style={{
                    width: '100%', height: 38,
                    background: T.accentDim, border: `1px solid ${T.border}`,
                    color: T.accent, borderRadius: 10, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    transition: 'all .2s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = T.accentMid; e.currentTarget.style.borderColor = T.accent; }}
                  onMouseLeave={e => { e.currentTarget.style.background = T.accentDim; e.currentTarget.style.borderColor = T.border; }}
                >
                  <Plus size={16} />
                </button>
              ) : (
                <button
                  onClick={goBack}
                  style={{
                    width: '100%', display: 'flex', alignItems: 'center', gap: 9,
                    background: 'linear-gradient(135deg, rgba(100,255,218,0.12), rgba(100,255,218,0.06))',
                    border: `1px solid ${T.border}`, color: T.accent,
                    padding: '10px 14px', borderRadius: 10, cursor: 'pointer',
                    fontSize: 13, fontWeight: 500, fontFamily: "'DM Sans', sans-serif",
                    transition: 'all .2s', animation: 'fadeIn .25s ease',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = T.accent; e.currentTarget.style.background = T.accentMid; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.background = 'linear-gradient(135deg, rgba(100,255,218,0.12), rgba(100,255,218,0.06))'; }}
                >
                  <Plus size={15} /> New Interview
                </button>
              )}
            </div>

            {/* History List */}
            <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
              {!sidebarCollapsed && (
                <div style={{
                  fontSize: 9, letterSpacing: 2.5, textTransform: 'uppercase',
                  color: T.muted, padding: '10px 18px 6px', fontWeight: 600, opacity: 0.7,
                }}>History</div>
              )}

              {interviews.length === 0 && !sidebarCollapsed && (
                <div style={{
                  padding: '24px 18px', textAlign: 'center',
                  color: T.muted, fontSize: 12, lineHeight: 1.7, opacity: 0.7,
                }}>
                  No interviews yet.<br />Start one to see it here.
                </div>
              )}

              {interviews.map((iv, idx) => (
                <HistoryItem
                  key={iv.id} iv={iv}
                  isActive={currentInterview?.id === iv.id}
                  collapsed={sidebarCollapsed}
                  formatDate={formatDate} msgPreview={msgPreview}
                  onLoad={() => loadInterview(iv)}
                  onDeleteRequest={() => setDeleteConfirm(iv.id)}
                  confirmingDelete={deleteConfirm === iv.id}
                  onConfirmDelete={() => deleteInterview(iv.id)}
                  onCancelDelete={() => setDeleteConfirm(null)}
                  idx={idx}
                />
              ))}
            </div>
          </aside>

          {/* ══════════ MAIN CONTENT ══════════ */}
          <main style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            overflow: 'hidden', position: 'relative', minWidth: 0,
          }}>

            {/* ── HOME SCREEN ── */}
            {!currentInterview && (
              <div style={{
                flex: 1, display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                padding: '40px 32px', animation: 'fadeUp .5s ease both', overflow: 'auto',
              }}>
                <div style={{
                  position: 'absolute', top: '20%', left: '50%', transform: 'translateX(-50%)',
                  width: 340, height: 340,
                  background: 'radial-gradient(circle, rgba(100,255,218,0.04) 0%, transparent 70%)',
                  pointerEvents: 'none', borderRadius: '50%',
                }} />
                <h1 style={{
                  fontFamily: "'Syne', sans-serif", fontWeight: 800,
                  fontSize: 'clamp(26px, 3.8vw, 48px)', textAlign: 'center',
                  color: T.accent, textShadow: `0 0 40px ${T.accentGlow}`,
                  marginBottom: 12, lineHeight: 1.1, position: 'relative',
                }}>
                  Mock Interview
                </h1>
                <p style={{
                  color: T.muted, fontSize: 14, textAlign: 'center',
                  maxWidth: 420, lineHeight: 1.8, marginBottom: 52, position: 'relative',
                }}>
                  Practice with your <span style={{ color: T.accent, fontWeight: 600 }}>AI interviewer</span> and ace your next interview.
                </p>
                <div style={{
                  display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: 24, width: '100%', maxWidth: 580, position: 'relative',
                }}>
                  <InterviewCard
                    onClick={() => startNewInterview('technical')}
                    icon={<MessageCircle size={38} color={T.accent} />}
                    label="Technical"
                    badge="DSA · System Design · Coding"
                    desc="Problem-solving, algorithms, architecture & coding challenges."
                  />
                  <InterviewCard
                    onClick={() => startNewInterview('hr')}
                    icon={<User size={38} color={T.accent} />}
                    label="HR / Behavioural"
                    badge="Soft Skills · Culture Fit"
                    desc="Behavioural questions, communication & career goals."
                  />
                </div>
              </div>
            )}

            {/* ── CHAT SCREEN ── */}
            {currentInterview && (
              <div style={{
                flex: 1, display: 'flex', flexDirection: 'column',
                overflow: 'hidden', animation: 'fadeIn .3s ease',
              }}>
                {/* Chat top bar */}
                <div style={{
                  padding: '14px 28px',
                  borderBottom: `1px solid ${T.sidebarBdr}`,
                  background: 'rgba(4,11,24,0.6)', backdropFilter: 'blur(12px)',
                  display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0,
                }}>
                  <span style={{
                    fontSize: 10, letterSpacing: 2.5, textTransform: 'uppercase',
                    color: T.accent, border: `1px solid ${T.border}`,
                    padding: '4px 14px', borderRadius: 20,
                    background: T.accentDim, fontWeight: 600,
                  }}>
                    {interviewType} Interview
                  </span>
                  <span style={{ fontSize: 12, color: T.muted }}>
                    {formatDate(currentInterview.timestamp)}
                  </span>
                  <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 10 }}>
                    {isSpeaking && (
                      <button
                        onClick={stopSpeaking}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 6,
                          background: 'none', border: `1px solid ${T.border}`,
                          color: T.muted, borderRadius: 8, padding: '5px 12px',
                          cursor: 'pointer', fontSize: 12, transition: 'all .2s',
                          fontFamily: "'DM Sans', sans-serif",
                        }}
                        onMouseEnter={e => { e.currentTarget.style.borderColor = T.accentGlow; e.currentTarget.style.color = T.accent; }}
                        onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.muted; }}
                      >
                        <VolumeX size={13} /> Stop
                      </button>
                    )}
                    {isLoading && <LoadingDots />}
                  </div>
                </div>

                {/* Messages */}
                <div style={{
                  flex: 1, overflowY: 'auto',
                  padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 16,
                }}>
                  {messages.map((msg, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                        gap: 10, animation: 'fadeUp .3s ease both',
                        animationDelay: `${i * 0.02}s`, alignItems: 'flex-end',
                      }}
                    >
                      <div style={{
                        width: 30, height: 30, borderRadius: '50%',
                        background: msg.role === 'user'
                          ? 'linear-gradient(135deg, #0d3a6e, #0f5499)' : T.accentDim,
                        border: `1px solid ${T.border}`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                      }}>
                        {msg.role === 'user'
                          ? <User size={13} color={T.accent} />
                          : <MessageCircle size={13} color={T.accent} />
                        }
                      </div>
                      <div style={{
                        maxWidth: 'min(68%, 560px)', padding: '12px 18px',
                        borderRadius: msg.role === 'user' ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
                        background: msg.role === 'user' ? T.userBubble : T.aiBubble,
                        border: `1px solid ${msg.role === 'user' ? 'rgba(100,255,218,0.15)' : T.border}`,
                        fontSize: 14, lineHeight: 1.75, color: T.text,
                        boxShadow: msg.role === 'user'
                          ? '0 4px 20px rgba(13,58,110,0.4)' : '0 4px 20px rgba(0,0,0,0.4)',
                      }}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* ── MIC CONTROL BAR ── */}
                <div style={{
                  padding: '18px 28px 24px',
                  borderTop: `1px solid ${T.sidebarBdr}`,
                  background: 'rgba(4,11,24,0.7)', backdropFilter: 'blur(12px)',
                  display: 'flex', flexDirection: 'column', alignItems: 'center',
                  gap: 12, flexShrink: 0,
                }}>
                  {/* Live transcript — shows what user is saying in real-time */}
                  {liveTranscript && (
                    <div style={{
                      fontSize: 13, color: T.subtle, fontStyle: 'italic',
                      maxWidth: 500, width: '100%', textAlign: 'center',
                      background: T.accentDim, border: `1px solid ${T.border}`,
                      padding: '8px 18px', borderRadius: 10, lineHeight: 1.6,
                      animation: 'fadeIn .2s ease',
                    }}>
                      "{liveTranscript}"
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                    {/* Mic button */}
                    <button
                      onClick={toggleListening}
                      disabled={isLoading}
                      title={isListening ? 'Stop & Send' : 'Start Speaking'}
                      style={{
                        width: 62, height: 62, borderRadius: '50%',
                        border: `2px solid ${isListening ? T.accent : T.border}`,
                        background: isListening ? T.accentMid : 'rgba(8,18,36,0.9)',
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        animation: isListening ? 'pulseRing 1.4s infinite' : 'none',
                        transition: 'all .3s',
                        boxShadow: isListening
                          ? `0 0 30px ${T.accentGlow}`
                          : '0 4px 20px rgba(0,0,0,0.4)',
                        opacity: isLoading ? 0.45 : 1,
                      }}
                      onMouseEnter={e => {
                        if (!isLoading && !isListening) {
                          e.currentTarget.style.borderColor = T.accentGlow;
                          e.currentTarget.style.background  = T.accentDim;
                        }
                      }}
                      onMouseLeave={e => {
                        if (!isListening) {
                          e.currentTarget.style.borderColor = T.border;
                          e.currentTarget.style.background  = 'rgba(8,18,36,0.9)';
                        }
                      }}
                    >
                      {isListening
                        ? <MicOff size={24} color={T.accent} />
                        : <Mic    size={24} color={isLoading ? T.muted : T.accent} />
                      }
                    </button>

                    <div style={{ textAlign: 'left' }}>
                      <div style={{
                        fontSize: 13,
                        color: isListening ? T.accent : T.subtle,
                        fontWeight: 500, transition: 'color .2s',
                      }}>
                        {isListening
                          ? '🎙 Listening… tap to send'
                          : isLoading ? 'Processing…' : 'Tap mic to speak'
                        }
                      </div>
                      <div style={{ fontSize: 11, color: T.muted, marginTop: 2 }}>
                        {isListening
                          ? 'Mic stays on — tap again when done'
                          : 'Mic off — tap to start speaking'
                        }
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>

        </div> {/* end sidebar+main row */}
      </div>
    </>
  );
}

/* ════════════════════════════════════════
   HISTORY ITEM
════════════════════════════════════════ */
function HistoryItem({ iv, isActive, collapsed, formatDate, msgPreview, onLoad, onDeleteRequest, confirmingDelete, onConfirmDelete, onCancelDelete, idx }) {
  const [hovered, setHovered] = useState(false);

  if (collapsed) {
    return (
      <div
        title={iv.title} onClick={onLoad}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '3px 8px', padding: '9px 0', borderRadius: 8, cursor: 'pointer',
          background: isActive ? 'rgba(100,255,218,0.12)' : hovered ? 'rgba(100,255,218,0.06)' : 'transparent',
          border: `1px solid ${isActive ? 'rgba(100,255,218,0.3)' : 'transparent'}`,
          transition: 'all .2s',
        }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        {iv.type === 'technical'
          ? <MessageCircle size={14} color={isActive ? '#64ffda' : '#7899bb'} />
          : <User          size={14} color={isActive ? '#64ffda' : '#7899bb'} />
        }
      </div>
    );
  }

  return (
    <div
      style={{
        margin: '2px 8px', borderRadius: 10,
        border: `1px solid ${isActive ? 'rgba(100,255,218,0.28)' : hovered ? 'rgba(100,255,218,0.12)' : 'transparent'}`,
        background: isActive ? 'rgba(100,255,218,0.07)' : hovered ? 'rgba(100,255,218,0.04)' : 'transparent',
        transition: 'all .2s', animation: 'slideIn .3s ease both',
        animationDelay: `${idx * 0.04}s`, position: 'relative', overflow: 'hidden',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {confirmingDelete ? (
        <div style={{ padding: '10px 12px' }}>
          <p style={{ fontSize: 11, color: '#ff8080', marginBottom: 8, lineHeight: 1.5 }}>
            Delete this interview?
          </p>
          <div style={{ display: 'flex', gap: 6 }}>
            <button
              onClick={onConfirmDelete}
              style={{
                flex: 1, fontSize: 11, padding: '5px 0',
                background: 'rgba(255,80,80,0.15)', border: '1px solid rgba(255,80,80,0.4)',
                color: '#ff8080', borderRadius: 6, cursor: 'pointer',
                fontFamily: "'DM Sans', sans-serif", transition: 'all .15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,80,80,0.25)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,80,80,0.15)'; }}
            >Delete</button>
            <button
              onClick={onCancelDelete}
              style={{
                flex: 1, fontSize: 11, padding: '5px 0',
                background: 'rgba(100,255,218,0.08)', border: '1px solid rgba(100,255,218,0.2)',
                color: '#7899bb', borderRadius: 6, cursor: 'pointer',
                fontFamily: "'DM Sans', sans-serif", transition: 'all .15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = '#64ffda'; }}
              onMouseLeave={e => { e.currentTarget.style.color = '#7899bb'; }}
            >Cancel</button>
          </div>
        </div>
      ) : (
        <div
          onClick={onLoad}
          style={{ padding: '10px 12px', cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: 5 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              {iv.type === 'technical'
                ? <MessageCircle size={11} color={isActive ? '#64ffda' : '#7899bb'} />
                : <User          size={11} color={isActive ? '#64ffda' : '#7899bb'} />
              }
              <span style={{
                fontSize: 11, fontWeight: 600, letterSpacing: 0.5,
                color: isActive ? '#64ffda' : '#a8c0d6', textTransform: 'capitalize',
              }}>
                {iv.type}
              </span>
            </div>
            {hovered && (
              <button
                onClick={(e) => { e.stopPropagation(); onDeleteRequest(); }}
                title="Delete"
                style={{
                  background: 'none', border: 'none', color: '#7899bb', cursor: 'pointer',
                  padding: '2px 4px', borderRadius: 4, display: 'flex', alignItems: 'center',
                  transition: 'color .15s', animation: 'fadeIn .15s ease',
                }}
                onMouseEnter={e => { e.currentTarget.style.color = '#ff8080'; }}
                onMouseLeave={e => { e.currentTarget.style.color = '#7899bb'; }}
              >
                <Trash2 size={12} />
              </button>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Clock size={9} color="#7899bb" />
            <span style={{ fontSize: 10, color: '#7899bb' }}>{formatDate(iv.timestamp)}</span>
          </div>
          <p style={{
            fontSize: 11, color: isActive ? '#a8c0d6' : '#5a7a95',
            lineHeight: 1.5, marginTop: 1,
            overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis',
          }}>
            {msgPreview(iv)}
          </p>
        </div>
      )}
    </div>
  );
}

/* ════════════════════════════════════════
   INTERVIEW CARD
════════════════════════════════════════ */
function InterviewCard({ onClick, icon, label, badge, desc }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: hovered ? 'rgba(100,255,218,0.07)' : 'rgba(8,18,36,0.75)',
        border: `1px solid ${hovered ? 'rgba(100,255,218,0.45)' : 'rgba(99,255,218,0.15)'}`,
        borderRadius: 20, padding: '36px 28px', cursor: 'pointer',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        textAlign: 'center', minHeight: 240, justifyContent: 'center',
        boxShadow: hovered
          ? '0 20px 50px rgba(0,0,0,0.6), 0 0 30px rgba(100,255,218,0.12)'
          : '0 12px 36px rgba(0,0,0,0.4)',
        transform: hovered ? 'translateY(-8px) scale(1.02)' : 'none',
        transition: 'all .3s cubic-bezier(.4,0,.2,1)',
        animation: 'fadeUp .6s ease both',
      }}
    >
      <div style={{
        width: 68, height: 68, borderRadius: '50%',
        background: 'rgba(100,255,218,0.08)', border: '1px solid rgba(99,255,218,0.18)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 18,
        boxShadow: hovered ? '0 0 24px rgba(100,255,218,0.3)' : 'none',
        transition: 'box-shadow .3s',
      }}>
        {icon}
      </div>
      <h3 style={{
        fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 18,
        color: '#64ffda', marginBottom: 8,
        textShadow: hovered ? '0 0 16px rgba(100,255,218,0.4)' : 'none',
        transition: 'text-shadow .3s',
      }}>
        {label}
      </h3>
      <span style={{
        fontSize: 10, letterSpacing: 1.5, textTransform: 'uppercase',
        color: '#7899bb', marginBottom: 10, fontWeight: 600,
      }}>
        {badge}
      </span>
      <p style={{ color: '#5a7a95', fontSize: 12, lineHeight: 1.7 }}>{desc}</p>
    </div>
  );
}

/* ════════════════════════════════════════
   SIDEBAR BUTTON
════════════════════════════════════════ */
function SidebarBtn({ icon, label, collapsed, onClick, title }) {
  const [hovered, setHovered] = useState(false);
  const base = {
    background: hovered ? 'rgba(100,255,218,0.16)' : 'rgba(100,255,218,0.08)',
    border: `1px solid ${hovered ? '#64ffda' : 'rgba(99,255,218,0.15)'}`,
    color: '#64ffda', cursor: 'pointer', transition: 'all .2s',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  };
  return collapsed ? (
    <button
      title={title} onClick={onClick}
      style={{ ...base, width: '100%', height: 36, borderRadius: 8 }}
      onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
    >{icon}</button>
  ) : (
    <button
      onClick={onClick}
      style={{
        ...base, width: '100%', gap: 8, justifyContent: 'flex-start',
        padding: '9px 14px', borderRadius: 10,
        fontSize: 13, fontWeight: 500, fontFamily: "'DM Sans', sans-serif",
      }}
      onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
    >
      {icon}{label}
    </button>
  );
}

/* ════════════════════════════════════════
   LOADING DOTS
════════════════════════════════════════ */
function LoadingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: 4, alignItems: 'center' }}>
      {[0, 1, 2].map(i => (
        <span key={i} style={{
          width: 5, height: 5, borderRadius: '50%', background: '#64ffda',
          display: 'inline-block',
          animation: `dotPulse 1.1s ${i * 0.18}s infinite alternate`,
        }} />
      ))}
    </span>
  );
}