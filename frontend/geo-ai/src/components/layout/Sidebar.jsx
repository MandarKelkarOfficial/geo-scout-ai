import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useSession } from '../../context/SessionContext';
import { useChat } from '../../context/ChatContext';
import Button from '../ui/Button';
import { useToast } from '../ui/Toast';

function groupByDate(sessions) {
  const today = new Date(); today.setHours(0,0,0,0);
  const yesterday = new Date(today); yesterday.setDate(yesterday.getDate()-1);
  const groups = { Today: [], Yesterday: [], Older: [] };
  for (const s of sessions) {
    const d = new Date(s.created_at);
    if (d >= today) groups.Today.push(s);
    else if (d >= yesterday) groups.Yesterday.push(s);
    else groups.Older.push(s);
  }
  return groups;
}

export default function Sidebar({ collapsed, onToggle }) {
  const { user } = useAuth();
  const { sessions, activeSessionToken, refreshSessions, removeSession, renameSession } = useSession();
  const { clearMessages } = useChat();
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => { if (user) refreshSessions(); }, [user]);

  const handleNew = () => { clearMessages(); navigate('/chat'); };
  const handleSelect = (s) => navigate(`/chat/${s.session_token}`);
  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!confirm('Delete this chat?')) return;
    await removeSession(id);
    toast('Chat deleted', 'info');
  };
  const handleRename = async (e, id) => {
    e.stopPropagation();
    if (editTitle.trim()) await renameSession(id, editTitle.trim());
    setEditingId(null);
  };

  const groups = groupByDate(sessions);

  if (collapsed) {
    return (
      <div className="w-14 h-full bg-surface border-r border-border flex flex-col items-center py-4 gap-3">
        <button onClick={onToggle} className="text-muted hover:text-gray-100 p-2 rounded-lg hover:bg-surface-hover">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
        </button>
        <button onClick={handleNew} className="text-accent hover:text-accent-hover p-2 rounded-lg hover:bg-surface-hover">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
        </button>
      </div>
    );
  }

  return (
    <div className="w-64 h-full bg-surface border-r border-border flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-border">
        <span className="font-semibold text-sm text-gray-100 flex items-center gap-2">
          <span className="text-accent text-lg">◎</span> GeoAI
        </span>
        <button onClick={onToggle} className="text-muted hover:text-gray-100 p-1 rounded-lg hover:bg-surface-hover">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" /></svg>
        </button>
      </div>

      {/* New chat */}
      <div className="px-3 py-3">
        <Button onClick={handleNew} className="w-full gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          New Chat
        </Button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-2 pb-3">
        {!user ? (
          <p className="text-xs text-muted text-center mt-4 px-2">Sign in to save your chats</p>
        ) : sessions.length === 0 ? (
          <p className="text-xs text-muted text-center mt-4">No chats yet</p>
        ) : (
          Object.entries(groups).map(([label, items]) =>
            items.length > 0 && (
              <div key={label} className="mb-3">
                <p className="text-xs text-muted px-2 py-1 uppercase tracking-wider">{label}</p>
                {items.map(s => (
                  <div
                    key={s.id}
                    onClick={() => handleSelect(s)}
                    className={`group flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer text-sm transition-colors ${
                      activeSessionToken === s.session_token ? 'bg-surface-hover text-gray-100' : 'text-muted hover:bg-surface-hover hover:text-gray-100'
                    }`}
                  >
                    {editingId === s.id ? (
                      <input
                        autoFocus
                        value={editTitle}
                        onChange={e => setEditTitle(e.target.value)}
                        onBlur={e => handleRename(e, s.id)}
                        onKeyDown={e => e.key === 'Enter' && handleRename(e, s.id)}
                        onClick={e => e.stopPropagation()}
                        className="flex-1 bg-transparent border-b border-accent outline-none text-gray-100 text-sm"
                      />
                    ) : (
                      <span className="flex-1 truncate">{s.title || 'Untitled chat'}</span>
                    )}
                    <div className="hidden group-hover:flex gap-1 shrink-0">
                      <button onClick={e => { e.stopPropagation(); setEditingId(s.id); setEditTitle(s.title || ''); }} className="p-0.5 text-muted hover:text-gray-100">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                      </button>
                      <button onClick={e => handleDelete(e, s.id)} className="p-0.5 text-muted hover:text-red-400">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )
          )
        )}
      </div>

      {/* Nav links */}
      <div className="border-t border-border px-3 py-3 space-y-1">
        {user && (
          <>
            <button onClick={() => navigate('/history')} className="w-full flex items-center gap-2 px-2 py-2 text-sm text-muted hover:text-gray-100 hover:bg-surface-hover rounded-lg transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              History
            </button>
            <button onClick={() => navigate('/profile')} className="w-full flex items-center gap-2 px-2 py-2 text-sm text-muted hover:text-gray-100 hover:bg-surface-hover rounded-lg transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
              Profile
            </button>
          </>
        )}
        {!user && (
          <button onClick={() => navigate('/login')} className="w-full flex items-center gap-2 px-2 py-2 text-sm text-accent hover:bg-surface-hover rounded-lg transition-colors font-medium">
            Sign In
          </button>
        )}
      </div>
    </div>
  );
}
