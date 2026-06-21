import { createContext, useContext, useState, useCallback } from 'react';
import * as sessionsApi from '../api/sessions';

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [sessions, setSessions] = useState([]);
  const [activeSessionToken, setActiveSessionToken] = useState(null);

  const refreshSessions = useCallback(async () => {
    try {
      const data = await sessionsApi.listSessions();
      setSessions(data);
    } catch {
      setSessions([]);
    }
  }, []);

  const removeSession = async (id) => {
    await sessionsApi.deleteSession(id);
    setSessions(prev => prev.filter(s => s.id !== id));
  };

  const renameSession = async (id, title) => {
    const updated = await sessionsApi.renameSession(id, title);
    setSessions(prev => prev.map(s => s.id === id ? updated : s));
    return updated;
  };

  return (
    <SessionContext.Provider value={{
      sessions, activeSessionToken, setActiveSessionToken,
      refreshSessions, removeSession, renameSession
    }}>
      {children}
    </SessionContext.Provider>
  );
}

export const useSession = () => useContext(SessionContext);
