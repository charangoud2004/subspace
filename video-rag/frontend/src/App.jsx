import { useState, useMemo } from 'react';
import IngestForm from './components/IngestForm';
import VideoCard from './components/VideoCard';
import ChatPanel from './components/ChatPanel';

export default function App() {
  const sessionId = useMemo(() => crypto.randomUUID(), []);
  const [ingested, setIngested] = useState(false);
  const [videoData, setVideoData] = useState({ A: null, B: null });

  const handleIngested = (data) => {
    setVideoData({ A: data.video_a, B: data.video_b });
    setIngested(true);
  };

  return (
    <div className="min-h-screen bg-surface-950 relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-600/8 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/8 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-accent-500/3 to-transparent rounded-full" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Navbar */}
        <nav className="border-b border-surface-800/50 backdrop-blur-md bg-surface-950/80 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <span className="font-bold text-surface-200 tracking-tight">Video RAG</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-surface-500 font-mono">
                session: {sessionId.slice(0, 8)}
              </span>
              {ingested && (
                <button
                  onClick={() => {
                    setIngested(false);
                    setVideoData({ A: null, B: null });
                  }}
                  className="text-xs text-surface-500 hover:text-surface-300 transition-colors flex items-center gap-1"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  New Session
                </button>
              )}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          {!ingested ? (
            <div className="flex items-center justify-center min-h-[70vh]">
              <IngestForm onIngested={handleIngested} sessionId={sessionId} />
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Video Cards - Left Side */}
              <div className="lg:col-span-5 space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <h2 className="text-lg font-semibold text-surface-300">Video Comparison</h2>
                  <span className="px-2 py-0.5 rounded-md text-xs bg-surface-800 text-surface-500">2 videos</span>
                </div>
                {videoData.A && <VideoCard video={videoData.A} label="A" />}
                {videoData.B && <VideoCard video={videoData.B} label="B" />}
              </div>

              {/* Chat Panel - Right Side */}
              <div className="lg:col-span-7">
                <div className="flex items-center gap-2 mb-2">
                  <h2 className="text-lg font-semibold text-surface-300">AI Analysis</h2>
                  <span className="px-2 py-0.5 rounded-md text-xs bg-accent-500/10 text-accent-400">RAG</span>
                </div>
                <ChatPanel sessionId={sessionId} />
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-surface-800/30 mt-16">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between text-xs text-surface-600">
            <span>Video RAG v1.0 — AI-Powered Video Comparison</span>
            <span>Built with FastAPI, LangChain, Gemini & React</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
