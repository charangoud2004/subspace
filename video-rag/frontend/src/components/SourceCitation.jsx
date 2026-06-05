import { useState } from 'react';

export default function SourceCitation({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  const getVideoLabel = (videoId) => {
    // Heuristic: if it looks like a YouTube ID (11 chars alphanumeric), label as A
    // Otherwise label as B (Instagram)
    if (videoId && videoId.length === 11 && /^[a-zA-Z0-9_-]+$/.test(videoId)) {
      return { label: 'Video A', icon: '🎬', color: 'text-youtube' };
    }
    return { label: 'Video B', icon: '📱', color: 'text-instagram' };
  };

  return (
    <div className="mt-2 animate-fade-in">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-surface-500 hover:text-surface-300 transition-colors"
      >
        <svg
          className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-90' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span>📎 {sources.length} source{sources.length > 1 ? 's' : ''} cited</span>
      </button>

      {expanded && (
        <div className="mt-2 space-y-1.5 pl-5">
          {sources.map((src, i) => {
            const { label, icon, color } = getVideoLabel(src.video_id);
            return (
              <div
                key={i}
                className="flex items-start gap-2 p-2.5 rounded-lg bg-surface-800/40 border border-surface-700/30 text-xs"
              >
                <span className="flex-shrink-0 mt-0.5">{icon}</span>
                <div className="min-w-0">
                  <span className={`font-semibold ${color}`}>{label}</span>
                  <span className="text-surface-500"> — Chunk {src.chunk_index + 1}</span>
                  <p className="text-surface-400 mt-0.5 line-clamp-2 italic">
                    "{src.preview}..."
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
