import { useState } from 'react';

const SUGGESTED_QUESTIONS = [
  "Compare the engagement rates of both videos",
  "Which video has a more effective content strategy?",
  "Summarize the key topics discussed in each video",
  "What hashtag strategies are each creator using?",
  "Which creator has better audience retention metrics?",
];

export default function IngestForm({ onIngested, sessionId }) {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [instagramUrl, setInstagramUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!youtubeUrl.trim() || !instagramUrl.trim()) {
      setError('Both URLs are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          youtube_url: youtubeUrl.trim(),
          instagram_url: instagramUrl.trim(),
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      const data = await res.json();
      onIngested(data);
    } catch (err) {
      setError(err.message || 'Failed to ingest videos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent-500/10 border border-accent-500/20 text-accent-400 text-sm font-medium mb-6">
          <span className="w-2 h-2 rounded-full bg-accent-400 animate-pulse" />
          AI-Powered Video Analysis
        </div>
        <h1 className="text-5xl font-extrabold gradient-text mb-4 tracking-tight">
          Video RAG
        </h1>
        <p className="text-surface-400 text-lg max-w-2xl mx-auto text-balance">
          Compare any YouTube video with an Instagram reel using retrieval-augmented generation. 
          Paste both URLs below to start analyzing.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* YouTube Input */}
          <div className="space-y-2">
            <label htmlFor="youtube-url" className="flex items-center gap-2 text-sm font-medium text-surface-300">
              <svg className="w-5 h-5 text-youtube" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              YouTube Video
            </label>
            <input
              id="youtube-url"
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              className="input-field"
              disabled={loading}
            />
          </div>

          {/* Instagram Input */}
          <div className="space-y-2">
            <label htmlFor="instagram-url" className="flex items-center gap-2 text-sm font-medium text-surface-300">
              <svg className="w-5 h-5 text-instagram" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
              </svg>
              Instagram Reel
            </label>
            <input
              id="instagram-url"
              type="url"
              value={instagramUrl}
              onChange={(e) => setInstagramUrl(e.target.value)}
              placeholder="https://instagram.com/reel/..."
              className="input-field"
              disabled={loading}
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-in">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          id="ingest-submit"
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-3 text-base"
        >
          {loading ? (
            <>
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Analyzing Videos...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Analyze & Compare
            </>
          )}
        </button>
      </form>

      {/* Suggested Questions Preview */}
      <div className="mt-8 text-center">
        <p className="text-surface-500 text-sm mb-3">After ingestion, ask things like:</p>
        <div className="flex flex-wrap justify-center gap-2">
          {SUGGESTED_QUESTIONS.slice(0, 3).map((q, i) => (
            <span key={i} className="px-3 py-1.5 rounded-lg bg-surface-800/50 border border-surface-700/30 text-surface-400 text-xs">
              "{q}"
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
