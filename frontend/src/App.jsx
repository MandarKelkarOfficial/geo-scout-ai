import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import { AuthProvider } from './context/AuthContext';
import { SessionProvider } from './context/SessionContext';
import { ChatProvider } from './context/ChatContext';
import { ToastProvider } from './components/ui/Toast';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ChatPage from './pages/ChatPage';
import ProfilePage from './pages/ProfilePage';
import HistoryPage from './pages/HistoryPage';
import SharedChatPage from './pages/SharedChatPage';

function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen bg-base flex items-center justify-center text-muted text-sm">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/chat/:sessionToken" element={<ChatPage />} />
      <Route path="/share/:token" element={<SharedChatPage />} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <SessionProvider>
            <ChatProvider>
              <AppRoutes />
            </ChatProvider>
          </SessionProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
