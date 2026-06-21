import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/ui/Toast';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ProfilePage() {
  const { user, updateProfile, logout } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateProfile(fullName);
      toast('Profile updated!', 'success');
    } catch {
      toast('Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  if (!user) { navigate('/login'); return null; }

  return (
    <div className="min-h-screen bg-base px-4 py-10">
      <div className="max-w-lg mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <button onClick={() => navigate(-1)} className="text-muted hover:text-gray-100">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          </button>
          <h1 className="text-lg font-semibold">Profile</h1>
        </div>

        {/* Avatar */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-full bg-accent flex items-center justify-center text-xl font-bold text-white">
            {(user.full_name?.slice(0,2) || user.email?.slice(0,2) || '??').toUpperCase()}
          </div>
          <div>
            <div className="font-medium text-gray-100">{user.full_name || 'No name set'}</div>
            <div className="text-sm text-muted">{user.email}</div>
          </div>
        </div>

        {/* Edit form */}
        <div className="bg-surface border border-border rounded-2xl p-6 mb-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">Account Details</h2>
          <form onSubmit={handleSave} className="flex flex-col gap-4">
            <Input label="Email" value={user.email} disabled className="opacity-60 cursor-not-allowed" />
            <Input label="Full Name" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Your name" />
            <Button type="submit" disabled={saving} className="self-start">
              {saving ? 'Saving…' : 'Save changes'}
            </Button>
          </form>
        </div>

        {/* Danger zone */}
        <div className="bg-surface border border-border rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-red-400 mb-4">Account Actions</h2>
          <Button variant="outline" onClick={handleLogout} className="border-red-900 text-red-400 hover:bg-red-900/20">
            Sign out
          </Button>
        </div>
      </div>
    </div>
  );
}
