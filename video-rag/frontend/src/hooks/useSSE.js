import { useState, useCallback, useRef } from 'react';

/**
 * Custom hook for Server-Sent Events streaming from the chat endpoint.
 * Returns streaming text, sources, loading state, and a trigger function.
 */
export default function useSSE() {
  const [streamingText, setStreamingText] = useState('');
  const [sources, setSources] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const eventSourceRef = useRef(null);

  const closeConnection = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const startStream = useCallback((message, sessionId) => {
    return new Promise((resolve) => {
      closeConnection();

      setStreamingText('');
      setSources([]);
      setIsStreaming(true);

      const params = new URLSearchParams({ message, session_id: sessionId });
      const url = `/api/chat/stream?${params.toString()}`;
      const es = new EventSource(url);
      eventSourceRef.current = es;

      let accumulated = '';

      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.done) {
            setSources(data.sources || []);
            setIsStreaming(false);
            es.close();
            eventSourceRef.current = null;
            resolve({ text: accumulated, sources: data.sources || [] });
          } else {
            accumulated += data.token;
            setStreamingText(accumulated);
          }
        } catch (err) {
          console.error('[useSSE] Parse error:', err);
        }
      };

      es.onerror = (err) => {
        console.error('[useSSE] Connection error:', err);
        setIsStreaming(false);
        es.close();
        eventSourceRef.current = null;
        resolve({ text: accumulated, sources: [] });
      };
    });
  }, [closeConnection]);

  return {
    streamingText,
    sources,
    isStreaming,
    startStream,
    closeConnection,
  };
}
