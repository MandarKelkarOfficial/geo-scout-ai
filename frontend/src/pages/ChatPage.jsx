import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import { useChat } from '../context/ChatContext';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/layout/Sidebar';
import TopBar from '../components/layout/TopBar';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import ThinkingDots from '../components/chat/ThinkingDots';

export default function ChatPage() {
  const { sessionToken } = useParams();
  const { user } = useAuth();
  const { sessions, activeSessionToken, setActiveSessionToken, refreshSessions } = useSession();
  const { messages, isThinking, sendMessage, loadHistory, clearMessages, currentSessionToken } = useChat();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const bottomRef = useRef(null);
  const navigate = useNavigate();

  // Load history when navigating to an existing session
  useEffect(() => {
    if (sessionToken) {
      setActiveSessionToken(sessionToken);
      const session = sessions.find(s => s.session_token === sessionToken);
      if (session) {
        loadHistory(session.id, sessionToken);
      } else if (user) {
        refreshSessions().then(() => {
          const found = sessions.find(s => s.session_token === sessionToken);
          if (found) loadHistory(found.id, sessionToken);
        });
      }
    } else {
      clearMessages();
      setActiveSessionToken(null);
    }
  }, [sessionToken, user]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  const handleSend = (query) => {
    sendMessage(query, (newToken) => {
      if (!sessionToken) {
        navigate(`/chat/${newToken}`, { replace: true });
      }
      if (user) refreshSessions();
    });
  };

  const currentSession = sessions.find(s => s.session_token === (sessionToken || currentSessionToken));

  const emptyState = (
    <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
      <div className="text-6xl mb-5 text-accent" style={{filter:'drop-shadow(0 0 20px #d97706aa)'}}>◎</div>
      <h2 className="text-2xl font-semibold text-gray-100 mb-2">What would you like to know?</h2>
      <p className="text-muted text-sm max-w-sm">Ask me about weather, places, real estate, geography — anything about any location on Earth.</p>
      <div className="grid grid-cols-2 gap-2 mt-8 max-w-sm w-full">
        {['Weather in Mumbai today?', 'Restaurants near Pune station', 'Real estate in Baner under ₹80L', 'Where is the Sahara Desert?'].map(q => (
          <button key={q} onClick={() => handleSend(q)} className="bg-surface border border-border hover:border-accent text-xs text-muted hover:text-gray-100 px-3 py-2.5 rounded-xl text-left transition-colors">
            {q}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-base overflow-hidden">
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(v => !v)} />
      <div className="flex flex-col flex-1 min-w-0">
        <TopBar sessionId={currentSession?.id} sessionTitle={currentSession?.title} />
        <div className="flex-1 overflow-y-auto py-4">
          {messages.length === 0 ? emptyState : (
            <>
              {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}
              {isThinking && (
                <div className="flex px-4 py-1.5">
                  <div className="w-7 h-7 rounded-full bg-accent flex items-center justify-center text-xs font-bold mr-2 mt-1 shrink-0">G</div>
                  <div className="bg-surface border-l-2 border-accent rounded-2xl rounded-tl-sm px-4 py-3">
                    <ThinkingDots />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </>
          )}
        </div>
        <ChatInput onSend={handleSend} disabled={isThinking} />
      </div>
    </div>
  );
}
