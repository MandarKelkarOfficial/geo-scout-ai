import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../assets/globe.css';
import Globe from '../components/Globe';

const FEATURES = [
  { icon: 'pin_drop', title: 'Geocoding', desc: 'Find any place on Earth instantly' },
  { icon: 'partly_cloudy_day', title: 'Live Weather', desc: 'Real-time weather for any location' },
  { icon: 'location_city', title: 'Nearby Places', desc: 'Hospitals, restaurants, parks & more' },
  { icon: 'real_estate_agent', title: 'Real Estate', desc: 'Property listings & market insights' },
  { icon: 'satellite_alt', title: 'Satellite View', desc: 'Aerial imagery & terrain data' },
  { icon: 'forum', title: 'Natural Language', desc: 'Just ask in plain English' },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div
      style={{ position: 'relative', minHeight: '100vh', background: '#06060f', color: '#f1f1f1', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
    >
      {/* ── FULL-SCREEN GLOBE LAYER ── */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 0,
          pointerEvents: 'none',
          overflow: 'hidden',
        }}
      >
        {/* Stars */}
        <div style={{
          position: 'absolute', inset: 0, opacity: 0.18,
          backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.7) 1px, transparent 1px)',
          backgroundSize: '55px 55px',
        }} />

        {/* Pure CSS Globe from globe.css */}
       <Globe />


        {/* Minimal top+bottom fade so nav/footer are readable */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(to bottom, rgba(6,6,15,0.65) 0%, transparent 20%, transparent 75%, rgba(6,6,15,0.80) 100%)',
          zIndex: 1,
        }} />
      </div>

      {/* ── NAV ── */}
      <nav style={{
        position: 'relative', zIndex: 10,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 32px',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
        backdropFilter: 'blur(8px)',
      }}>
        <span style={{ fontSize: 17, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: '#f59e0b', fontSize: 24, filter: 'drop-shadow(0 0 10px rgba(245,158,11,0.8))' }}>◎</span>
          GeoAI
        </span>
        <div style={{ display: 'flex', gap: 10 }}>
          {user ? (
            <button
              onClick={() => navigate('/chat')}
              className="bg-amber-500 hover:bg-amber-400 text-black px-5 py-2 rounded-xl text-sm font-semibold transition-all hover:scale-105"
              style={{ boxShadow: '0 0 18px rgba(245,158,11,0.45)' }}
            >
              Open Chat
            </button>
          ) : (
            <>
              <button onClick={() => navigate('/login')} className="text-gray-400 hover:text-white px-4 py-2 text-sm transition-colors">
                Sign In
              </button>
              <button
                onClick={() => navigate('/register')}
                className="bg-amber-500 hover:bg-amber-400 text-black px-5 py-2 rounded-xl text-sm font-semibold transition-all hover:scale-105"
                style={{ boxShadow: '0 0 18px rgba(245,158,11,0.45)' }}
              >
                Get Started
              </button>
            </>
          )}
        </div>
      </nav>

      {/* ── HERO ── */}
      <div style={{
        position: 'relative', zIndex: 10, flex: 1,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: '80px 24px', textAlign: 'center',
      }}>
        <div style={{ fontSize: 56, marginBottom: 16, filter: 'drop-shadow(0 0 28px rgba(245,158,11,0.75))', lineHeight: 1 }}>◎</div>

        <h1 style={{
          fontSize: 'clamp(2.4rem, 5vw, 3.6rem)', fontWeight: 800, lineHeight: 1.15,
          marginBottom: 18,
          background: 'linear-gradient(135deg, #fde68a 0%, #f59e0b 50%, #ea580c 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          filter: 'drop-shadow(0 2px 20px rgba(245,158,11,0.25))',
        }}>
          Ask anything about<br />any place on Earth
        </h1>

        <p style={{ color: '#d1d5db', fontSize: '1.05rem', maxWidth: 420, marginBottom: 36, lineHeight: 1.65 }}>
          GeoAI combines real-time data — weather, places, satellite imagery,
          real estate — with AI to answer your geographic questions instantly.
        </p>

        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', justifyContent: 'center' }}>
          <button
            onClick={() => navigate(user ? '/chat' : '/register')}
            className="bg-amber-500 hover:bg-amber-400 text-black font-bold transition-all hover:scale-105"
            style={{
              padding: '13px 36px', borderRadius: 14, fontSize: '1rem',
              boxShadow: '0 0 30px rgba(245,158,11,0.5)',
            }}
          >
            {user ? 'Continue Chatting' : 'Start for free'}
          </button>
          <button
            onClick={() => navigate('/chat')}
            style={{
              padding: '13px 36px', borderRadius: 14, fontSize: '1rem',
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(255,255,255,0.04)',
              backdropFilter: 'blur(10px)',
              color: '#d1d5db', cursor: 'pointer', transition: 'all .2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(245,158,11,0.5)'; e.currentTarget.style.color = '#fff'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)'; e.currentTarget.style.color = '#d1d5db'; }}
          >
            Try without account
          </button>
        </div>
      </div>

      {/* ── FEATURE CARDS ── */}
      <div style={{ position: 'relative', zIndex: 10, padding: '0 32px 64px' }}>
        <div style={{
          maxWidth: 900, margin: '0 auto',
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16,
        }}>
          {FEATURES.map(f => (
            <div
              key={f.title}
              style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.10)',
                borderRadius: 18, padding: '20px 20px',
                backdropFilter: 'blur(14px)',
                transition: 'border-color .2s, transform .2s, box-shadow .2s',
                cursor: 'default',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'rgba(245,158,11,0.55)';
                e.currentTarget.style.transform = 'translateY(-3px)';
                e.currentTarget.style.boxShadow = '0 10px 32px rgba(0,0,0,0.45)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.10)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div className="material-symbols-outlined" style={{ fontSize: '32px', marginBottom: '16px', color: '#f97316' }}>
                {f.icon}
              </div>
              <h3 style={{ fontWeight: 600, fontSize: 13, color: '#fff', marginBottom: 4 }}>{f.title}</h3>
              <p style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.55 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── FOOTER ── */}
      <footer style={{
        position: 'relative', zIndex: 10,
        textAlign: 'center', padding: '18px', fontSize: 11, color: '#4b5563',
        borderTop: '1px solid rgba(255,255,255,0.06)',
      }}>
        GeoAI — Powered by FastAPI + AI
      </footer>
    </div>
  );
}
