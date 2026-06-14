import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSharedChat } from '../api/share';
import { useToast } from '../components/ui/Toast';
import MessageBubble from '../components/chat/MessageBubble';
import Button from '../components/ui/Button';

export default function SharedChatPage() {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    getSharedChat(token)
      .then(setData)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [token]);

  const handleCopyAll = () => {
    if (!data) return;
    const text = data.messages.map(m =>
      `${m.role === 'user' ? 'You' : 'GeoAI'}: ${m.role === 'user' ? m.query_text : m.response_text}`
    ).join('\n\n');
    navigator.clipboard.writeText(text).then(() => toast('Chat copied to clipboard!', 'success'));
  };

  if (loading) return (
    <div className="min-h-screen bg-base flex items-center justify-center text-muted text-sm">Loading shared chat…</div>
  );

  if (notFound) return (
    <div className="min-h-screen bg-base flex flex-col items-center justify-center text-center px-6">
      <div className="text-4xl mb-4">🔍</div>
      <h2 className="text-lg font-semibold text-gray-100 mb-2">Chat not found</h2>
      <p className="text-muted text-sm mb-6">This shared conversation may have been deleted or the link is invalid.</p>
      <Button onClick={() => navigate('/')}>Go Home</Button>
    </div>
  );

  const messages = data.messages.map((m, i) => ({
    id: i,
    role: m.role,
    content: m.role === 'user' ? m.query_text : m.response_text,
    tools_used: m.tools_used || []
  }));

  return (
    <div className="min-h-screen bg-base flex flex-col">
      {/* Banner */}
      <div className="bg-surface border-b border-border px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-accent text-lg">◎</span>
          <div>
            <span className="text-xs text-muted">Shared conversation</span>
            {data.title && <div className="text-sm font-medium text-gray-100">{data.title}</div>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleCopyAll} className="flex items-center gap-1.5 text-xs text-muted hover:text-gray-100 px-3 py-1.5 rounded-lg hover:bg-surface-hover border border-border transition-colors">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
            Copy chat
          </button>
          <Button onClick={() => navigate('/')}>Try GeoAI</Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 py-6 max-w-3xl mx-auto w-full px-4">
        {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}
      </div>
    </div>
  );
}
