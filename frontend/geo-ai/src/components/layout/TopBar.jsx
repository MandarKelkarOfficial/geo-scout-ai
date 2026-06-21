import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useSession } from '../../context/SessionContext';
import { shareSession } from '../../api/sessions';
import { useToast } from '../ui/Toast';

export default function TopBar({ sessionId, sessionTitle }) {
  const { user, logout } = useAuth();
  const { refreshSessions } = useSession();
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const handleShare = async () => {
    if (!sessionId) { toast('Start a conversation first', 'info'); return; }
    try {
      const { share_token } = await shareSession(sessionId);
      const url = `${window.location.origin}/share/${share_token}`;
      await navigator.clipboard.writeText(url);
      toast('Share link copied to clipboard!', 'success');
    } catch {
      toast('Failed to generate share link', 'error');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const initials = user?.full_name?.split(' ').map(w => w[0]).join('').toUpperCase().slice(0,2)
    || user?.email?.slice(0,2).toUpperCase()
    || '?';

  return (
    <header className="h-12 border-b border-border flex items-center justify-between px-4 bg-base shrink-0">
      <div className="flex items-center gap-3 min-w-0">
        {sessionTitle && (
          <span className="text-sm text-muted truncate max-w-xs">{sessionTitle}</span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {sessionId && (
          <button
            onClick={handleShare}
            className="flex items-center gap-1.5 text-xs text-muted hover:text-gray-100 px-3 py-1.5 rounded-lg hover:bg-surface-hover transition-colors"
            title="Copy share link"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13" /></svg>
            Share
          </button>
        )}

        {user ? (
          <div className="relative">
            <button
              onClick={() => setShowMenu(v => !v)}
              className="w-8 h-8 rounded-full bg-accent text-white text-xs font-bold flex items-center justify-center hover:bg-accent-hover transition-colors"
            >
              {initials}
            </button>
            {showMenu && (
              <div className="absolute right-0 top-10 bg-surface border border-border rounded-xl shadow-xl py-1 w-40 z-50">
                <button onClick={() => { navigate('/profile'); setShowMenu(false); }} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-surface-hover">Profile</button>
                <button onClick={() => { navigate('/history'); setShowMenu(false); }} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-surface-hover">History</button>
                <hr className="border-border my-1" />
                <button onClick={handleLogout} className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-surface-hover">Sign out</button>
              </div>
            )}
          </div>
        ) : (
          <button onClick={() => navigate('/login')} className="text-xs text-accent hover:text-accent-hover font-medium px-3 py-1.5 border border-accent rounded-lg transition-colors">
            Sign In
          </button>
        )}
      </div>
    </header>
  );
}
