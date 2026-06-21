import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/ui/Toast';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast('Welcome back!', 'success');
      navigate('/chat');
    } catch (err) {
      toast(err.message || 'Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-base flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-5xl text-accent">◎</span>
          <h1 className="text-xl font-semibold text-gray-100 mt-3">Welcome back</h1>
          <p className="text-sm text-muted mt-1">Sign in to your GeoAI account</p>
        </div>
        <div className="bg-surface border border-border rounded-2xl p-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required />
            <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
            <Button type="submit" disabled={loading} className="w-full mt-2 py-2.5">
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
        </div>
        <p className="text-center text-sm text-muted mt-4">
          No account?{' '}
          <Link to="/register" className="text-accent hover:text-accent-hover font-medium">Create one</Link>
        </p>
        <p className="text-center text-xs text-muted mt-2">
          <button onClick={() => navigate('/chat')} className="hover:text-gray-100 transition-colors">Continue without account →</button>
        </p>
      </div>
    </div>
  );
}
