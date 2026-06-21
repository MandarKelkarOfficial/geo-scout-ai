import { createContext, useContext, useState, useCallback } from 'react';
import { sendMessage as sendMessageApi } from '../api/chat';
import { getHistory } from '../api/sessions';

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [currentSessionToken, setCurrentSessionToken] = useState(null);

  const loadHistory = useCallback(async (sessionId, sessionToken) => {
    setCurrentSessionToken(sessionToken);
    const logs = await getHistory(sessionId);
    // Convert logs to message pairs
    const msgs = [];
    for (const log of logs) {
      if (log.role === 'user') {
        msgs.push({ role: 'user', content: log.query_text, id: `u-${log.id}` });
      } else {
        msgs.push({
          role: 'assistant',
          content: log.response_text,
          tools_used: log.tools_used,
          id: `a-${log.id}`
        });
      }
    }
    setMessages(msgs);
  }, []);

  const sendMessage = useCallback(async (query, onSessionToken) => {
    const userMsg = { role: 'user', content: query, id: `u-${Date.now()}` };
    setMessages(prev => [...prev, userMsg]);
    setIsThinking(true);

    try {
      const response = await sendMessageApi(query, currentSessionToken);
      const assistantMsg = {
        role: 'assistant',
        content: response.answer,
        tools_used: response.tools_used,
        id: `a-${Date.now()}`
      };
      setMessages(prev => [...prev, assistantMsg]);

      if (response.session_token && response.session_token !== currentSessionToken) {
        setCurrentSessionToken(response.session_token);
        if (onSessionToken) onSessionToken(response.session_token);
      }
    } catch (err) {
      const errMsg = {
        role: 'assistant',
        content: `Sorry, something went wrong: ${err.message}`,
        tools_used: [],
        id: `err-${Date.now()}`
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsThinking(false);
    }
  }, [currentSessionToken]);

  const clearMessages = () => {
    setMessages([]);
    setCurrentSessionToken(null);
  };

  return (
    <ChatContext.Provider value={{
      messages, isThinking, currentSessionToken,
      sendMessage, loadHistory, clearMessages, setCurrentSessionToken
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export const useChat = () => useContext(ChatContext);
