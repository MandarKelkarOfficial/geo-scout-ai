import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSession } from '../context/SessionContext';
import { useToast } from '../components/ui/Toast';
import Button from '../components/ui/Button';

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function HistoryPage() {
  const { user } = useAuth();
  const { sessions, refreshSessions, removeSession } = useSession();
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => { if (user) refreshSessions(); else navigate('/login'); }, [user]);

  const handleDelete = async (id) => {
    if (!confirm('Delete this chat permanently?')) return;
    await removeSession(id);
    toast('Chat deleted', 'info');
  };

  return (
    <div className="min-h-screen bg-base px-4 py-10">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <button onClick={() => navigate(-1)} className="text-muted hover:text-gray-100">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          </button>
          <h1 className="text-lg font-semibold">Chat History</h1>
          <span className="ml-auto text-xs text-muted">{sessions.length} conversation{sessions.length !== 1 ? 's' : ''}</span>
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-4">💬</div>
            <p className="text-muted">No conversations yet</p>
            <Button onClick={() => navigate('/chat')} className="mt-4">Start a chat</Button>
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.map(s => (
              <div
                key={s.id}
                className="bg-surface border border-border hover:border-accent rounded-2xl px-5 py-4 flex items-center gap-4 cursor-pointer transition-colors group"
                onClick={() => navigate(`/chat/${s.session_token}`)}
              >
                <div className="w-9 h-9 rounded-full bg-[#1e2a3a] flex items-center justify-center text-accent shrink-0">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm text-gray-100 truncate">{s.title || 'Untitled chat'}</div>
                  <div className="text-xs text-muted">{formatDate(s.created_at)}</div>
                </div>
                <button
                  onClick={e => { e.stopPropagation(); handleDelete(s.id); }}
                  className="opacity-0 group-hover:opacity-100 text-muted hover:text-red-400 p-1 rounded transition-all"
                  title="Delete"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
