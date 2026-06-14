import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const FEATURES = [
  { icon: '📍', title: 'Geocoding', desc: 'Find any place on Earth instantly' },
  { icon: '🌤', title: 'Live Weather', desc: 'Real-time weather for any location' },
  { icon: '🏙', title: 'Nearby Places', desc: 'Hospitals, restaurants, parks & more' },
  { icon: '🏠', title: 'Real Estate', desc: 'Property listings & market insights' },
  { icon: '🛰', title: 'Satellite View', desc: 'Aerial imagery & terrain data' },
  { icon: '💬', title: 'Natural Language', desc: 'Just ask in plain English' },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-base text-gray-100 flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-border">
        <span className="text-lg font-semibold flex items-center gap-2">
          <span className="text-accent text-2xl">◎</span> GeoAI
        </span>
        <div className="flex gap-3">
          {user ? (
            <button onClick={() => navigate('/chat')} className="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors">
              Open Chat
            </button>
          ) : (
            <>
              <button onClick={() => navigate('/login')} className="text-muted hover:text-gray-100 px-4 py-2 text-sm transition-colors">Sign In</button>
              <button onClick={() => navigate('/register')} className="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                Get Started
              </button>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
        <div className="mb-6 text-7xl select-none" style={{filter:'drop-shadow(0 0 40px #d97706aa)'}}>◎</div>
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-amber-400 to-orange-300 bg-clip-text text-transparent leading-tight">
          Ask anything about<br />any place on Earth
        </h1>
        <p className="text-lg text-muted max-w-lg mb-10">
          GeoAI combines real-time data — weather, places, satellite imagery, real estate — with AI to answer your geographic questions instantly.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => navigate(user ? '/chat' : '/register')}
            className="bg-accent hover:bg-accent-hover text-white px-7 py-3 rounded-xl font-semibold text-base transition-all hover:scale-105"
          >
            {user ? 'Continue Chatting' : 'Start for free'}
          </button>
          <button
            onClick={() => navigate('/chat')}
            className="border border-border hover:border-muted text-muted hover:text-gray-100 px-7 py-3 rounded-xl font-medium text-base transition-colors"
          >
            Try without account
          </button>
        </div>
      </div>

      {/* Features grid */}
      <div className="px-8 pb-20">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-3 gap-4">
          {FEATURES.map(f => (
            <div key={f.title} className="bg-surface border border-border rounded-2xl p-5 hover:border-accent transition-colors">
              <div className="text-2xl mb-2">{f.icon}</div>
              <h3 className="font-semibold text-sm text-gray-100 mb-1">{f.title}</h3>
              <p className="text-xs text-muted">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <footer className="border-t border-border text-center py-5 text-xs text-muted">
        GeoAI — Powered by FastAPI + AI
      </footer>
    </div>
  );
}
