import { useState, useCallback, useRef } from 'react';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../authConfig';
const API_BASE = 'http://localhost:8000';

/**
 * Custom hook encapsulating all backend API communication
 * for the chatbot frontend.
 */
export default function useChat() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [healthStatus, setHealthStatus] = useState('checking');
  const [latency, setLatency] = useState(null);
  const [error, setError] = useState(null);

  // Track token usage across the session
  const [tokenStats, setTokenStats] = useState({ totalInput: 0, totalOutput: 0, totalTokens: 0, requests: 0 });

  const healthIntervalRef = useRef(null);
  
  const { instance, accounts } = useMsal();

  const fetchWithAuth = useCallback(async (endpoint, options = {}) => {
    if (accounts.length === 0) {
      throw new Error("User not authenticated");
    }
    
    try {
      // Attempt silent token acquisition
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0]
      });
      
      const headers = new Headers(options.headers || {});
      headers.append('Authorization', `Bearer ${response.accessToken}`);
      
      return fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });
    } catch (error) {
      console.error("Token acquisition failed:", error);
      throw error;
    }
  }, [instance, accounts]);

  // ──────── HEALTH CHECK ────────
  const checkHealth = useCallback(async () => {
    const start = Date.now();
    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
      const lat = Date.now() - start;
      if (res.ok) {
        setHealthStatus('online');
        setLatency(lat);
      } else {
        setHealthStatus('offline');
        setLatency(null);
      }
    } catch {
      setHealthStatus('offline');
      setLatency(null);
    }
  }, []);

  const startHealthCheck = useCallback(() => {
    checkHealth();
    if (healthIntervalRef.current) clearInterval(healthIntervalRef.current);
    healthIntervalRef.current = setInterval(checkHealth, 8000);
    return () => clearInterval(healthIntervalRef.current);
  }, [checkHealth]);

  // ──────── LOAD ALL SESSIONS ────────
  const loadSessions = useCallback(async () => {
    if (accounts.length === 0) return; // Wait for auth
    setIsLoading(true);
    try {
      const res = await fetchWithAuth(`/conversation/all_sessions`);
      if (!res.ok) throw new Error(`Failed to load sessions: ${res.status}`);
      const data = await res.json();

      // Transform the nested dict structure into an array
      const sessionList = Object.entries(data.sessions || {}).map(([sessionId, messagesDict]) => {
        const msgArray = Object.entries(messagesDict).map(([msgId, details]) => ({
          id: msgId,
          humanMessage: details.humanMessage,
          aiMessage: details.aiMessage,
          createdAt: details.createdAt,
        }));
        // Sort by createdAt
        msgArray.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

        const firstMsg = msgArray[0];
        const lastMsg = msgArray[msgArray.length - 1];

        return {
          id: sessionId,
          title: firstMsg?.humanMessage?.substring(0, 60) || 'New Chat',
          preview: lastMsg?.aiMessage?.substring(0, 80) || '',
          messageCount: msgArray.length,
          createdAt: firstMsg?.createdAt,
          updatedAt: lastMsg?.createdAt,
          messages: msgArray,
        };
      });

      // Sort sessions by most recent
      sessionList.sort((a, b) => new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0));
      setSessions(sessionList);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load sessions:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ──────── LOAD HISTORY FOR A SESSION ────────
  const loadHistory = useCallback(async (sessionId) => {
    setIsLoading(true);
    setActiveSessionId(sessionId);
    try {
      const res = await fetchWithAuth(`/conversation/history/${sessionId}`);
      if (!res.ok) throw new Error(`Failed to load history: ${res.status}`);
      const data = await res.json();

      const msgArray = Object.entries(data.messages || {}).map(([msgId, details]) => ({
        id: msgId,
        humanMessage: details.humanMessage,
        aiMessage: details.aiMessage,
        createdAt: details.createdAt,
      }));

      msgArray.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      setMessages(msgArray);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ──────── SEND MESSAGE ────────
  const sendMessage = useCallback(async (message, sessionId = null) => {
    setIsSending(true);
    setError(null);

    // Optimistically add user message
    const tempId = 'temp-' + Date.now();
    const userMsg = {
      id: tempId,
      humanMessage: message,
      aiMessage: null,
      createdAt: new Date().toISOString(),
      isPending: true,
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const body = { message };
      if (sessionId) body.session_id = sessionId;

      const res = await fetchWithAuth(`/conversation/agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);
      
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let returnedSessionId = null;
      let fullResponse = "";
      let finalData = null;
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // Keep the incomplete part
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6);
            if (!dataStr.trim()) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.done) {
                finalData = data;
                returnedSessionId = data.session_id;
              } else if (data.chunk) {
                fullResponse += data.chunk;
                
                // Incrementally update the UI with streaming chunks
                setMessages(prev =>
                  prev.map(m =>
                    m.id === tempId
                      ? { ...m, aiMessage: fullResponse }
                      : m
                  )
                );
              }
            } catch (e) {
              console.error("Error parsing stream chunk", e, dataStr);
            }
          }
        }
      }

      if (finalData) {
        // Finalize message state with token stats
        setMessages(prev =>
          prev.map(m =>
            m.id === tempId
              ? {
                  ...m,
                  aiMessage: finalData.response,
                  isPending: false,
                  tokens: {
                    input: finalData.input_token,
                    output: finalData.output_token,
                    total: finalData.total_token,
                  },
                }
              : m
          )
        );

        setTokenStats(prev => ({
          totalInput: prev.totalInput + (finalData.input_token || 0),
          totalOutput: prev.totalOutput + (finalData.output_token || 0),
          totalTokens: prev.totalTokens + (finalData.total_token || 0),
          requests: prev.requests + 1,
        }));
      }

      // If new session was created, update active session ID
      if (!sessionId && returnedSessionId) {
        setActiveSessionId(returnedSessionId);
      }

      // Refresh sessions list to show the new/updated session
      await loadSessions();

      return { sessionId: returnedSessionId, response: fullResponse };
    } catch (err) {
      setError(err.message);
      // Mark the message as errored
      setMessages(prev =>
        prev.map(m =>
          m.id === tempId
            ? { ...m, aiMessage: `⚠️ **Error:** ${err.message}`, isPending: false, isError: true }
            : m
        )
      );
      return null;
    } finally {
      setIsSending(false);
    }
  }, [loadSessions]);

  // ──────── DELETE SESSION ────────
  const deleteSession = useCallback(async (sessionId) => {
    try {
      const res = await fetchWithAuth(`/conversation/session/${sessionId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`Failed to delete: ${res.status}`);

      setSessions(prev => prev.filter(s => s.id !== sessionId));

      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setMessages([]);
      }
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, [activeSessionId]);

  // ──────── DELETE MESSAGE ────────
  const deleteMessage = useCallback(async (messageId) => {
    try {
      const res = await fetchWithAuth(`/conversation/message/${messageId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`Failed to delete message: ${res.status}`);

      setMessages(prev => prev.filter(m => m.id !== messageId));
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  // ──────── UPDATE MESSAGE ────────
  const updateMessage = useCallback(async (messageId, content, role = 'user') => {
    try {
      const body = role === 'user'
        ? { humanMessage: content }
        : { aiMessage: content };

      const res = await fetchWithAuth(`/conversation/message/${messageId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error(`Failed to update message: ${res.status}`);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  // ──────── START NEW CHAT ────────
  const startNewChat = useCallback(() => {
    setActiveSessionId(null);
    setMessages([]);
    setError(null);
  }, []);

  // ──────── CLEAR ERROR ────────
  const clearError = useCallback(() => setError(null), []);

  return {
    // State
    sessions,
    activeSessionId,
    messages,
    isLoading,
    isSending,
    healthStatus,
    latency,
    error,
    tokenStats,

    // Actions
    checkHealth,
    startHealthCheck,
    loadSessions,
    loadHistory,
    sendMessage,
    deleteSession,
    deleteMessage,
    updateMessage,
    startNewChat,
    clearError,
    setActiveSessionId,
  };
}
