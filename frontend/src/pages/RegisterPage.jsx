import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/ui/Toast';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) { toast('Password must be at least 8 characters', 'error'); return; }
    setLoading(true);
    try {
      await register(email, password, fullName || undefined);
      toast('Account created!', 'success');
      navigate('/chat');
    } catch (err) {
      toast(err.message || 'Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-base flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-5xl text-accent">◎</span>
          <h1 className="text-xl font-semibold text-gray-100 mt-3">Create your account</h1>
          <p className="text-sm text-muted mt-1">Free to use · No credit card required</p>
        </div>
        <div className="bg-surface border border-border rounded-2xl p-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input label="Full Name (optional)" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Jane Smith" />
            <Input label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required />
            <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min 8 characters" required />
            <Button type="submit" disabled={loading} className="w-full mt-2 py-2.5">
              {loading ? 'Creating account…' : 'Create account'}
            </Button>
          </form>
        </div>
        <p className="text-center text-sm text-muted mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-accent hover:text-accent-hover font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
