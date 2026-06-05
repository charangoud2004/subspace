import { useState, useRef, useEffect } from 'react';
import useSSE from '../hooks/useSSE';
import SourceCitation from './SourceCitation';

const SUGGESTED_QUESTIONS = [
  "Compare the engagement rates of both videos",
  "Which video has a more effective content strategy?",
  "Summarize the key topics discussed in each video",
  "What hashtag strategies are each creator using?",
  "Which creator has better audience retention metrics?",
];

export default function ChatPanel({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { streamingText, sources, isStreaming, startStream } = useSSE();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText]);

  const handleSend = async (text) => {
    const message = text || input.trim();
    if (!message || isStreaming) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: message }]);

    const result = await startStream(message, sessionId);

    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: result.text,
        sources: result.sources,
      },
    ]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isEmpty = messages.length === 0 && !isStreaming;

  return (
    <div className="glass-card flex flex-col h-[600px] animate-slide-up" style={{ animationDelay: '200ms' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-surface-700/50">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-surface-200">AI Analyst</h2>
          <p className="text-xs text-surface-500">Powered by Gemini 1.5 Flash</p>
        </div>
        {isStreaming && (
          <div className="ml-auto flex items-center gap-1.5 text-xs text-accent-400">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-400 animate-pulse" />
            Thinking...
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {isEmpty && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-500/20 to-purple-500/20 flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-surface-300 font-medium mb-2">Ready to analyze</h3>
            <p className="text-surface-500 text-sm mb-6 max-w-sm">
              Ask me anything about the two videos. I'll compare metrics, analyze content, and cite my sources.
            </p>
            <div className="space-y-2 w-full max-w-sm">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="w-full text-left px-4 py-2.5 rounded-xl bg-surface-800/40 border border-surface-700/30
                           text-sm text-surface-400 hover:text-surface-200 hover:bg-surface-800/60 hover:border-surface-600/50
                           transition-all duration-200"
                >
                  <span className="text-accent-400 mr-2">→</span>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-accent-600/20 border border-accent-500/20 text-surface-200 rounded-br-md'
                  : 'bg-surface-800/60 border border-surface-700/30 text-surface-300 rounded-bl-md'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.role === 'assistant' && msg.sources && (
                <SourceCitation sources={msg.sources} />
              )}
            </div>
          </div>
        ))}

        {/* Streaming bubble */}
        {isStreaming && streamingText && (
          <div className="flex justify-start">
            <div className="max-w-[85%] px-4 py-3 rounded-2xl rounded-bl-md bg-surface-800/60 border border-surface-700/30 text-surface-300 text-sm leading-relaxed">
              <div className="whitespace-pre-wrap">{streamingText}</div>
              <span className="inline-block w-1.5 h-4 bg-accent-400 animate-pulse ml-0.5 rounded-sm" />
            </div>
          </div>
        )}

        {/* Streaming indicator without text */}
        {isStreaming && !streamingText && (
          <div className="flex justify-start">
            <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-surface-800/60 border border-surface-700/30">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-surface-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-surface-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-surface-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-surface-700/50">
        <div className="flex items-center gap-3">
          <input
            ref={inputRef}
            id="chat-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the videos..."
            className="input-field flex-1"
            disabled={isStreaming}
          />
          <button
            id="chat-send"
            onClick={() => handleSend()}
            disabled={isStreaming || !input.trim()}
            className="btn-primary !px-4 !py-3"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
