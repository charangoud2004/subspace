export default function VideoCard({ video, label }) {
  const isYouTube = video.platform === 'youtube';
  const platformColor = isYouTube ? 'youtube' : 'instagram';
  const platformLabel = isYouTube ? 'YouTube' : 'Instagram';
  const videoLabel = isYouTube ? 'Video A' : 'Video B';

  const engagementColor = (rate) => {
    if (rate >= 10) return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
    if (rate >= 5) return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
    if (rate >= 2) return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
    return 'text-red-400 bg-red-400/10 border-red-400/20';
  };

  const fmt = (n) => {
    if (typeof n !== 'number') return '0';
    return n.toLocaleString();
  };

  return (
    <div className="glass-card-hover p-6 animate-slide-up" style={{ animationDelay: isYouTube ? '0ms' : '100ms' }}>
      {/* Header Badges */}
      <div className="flex items-center justify-between mb-4">
        <span className={`badge ${isYouTube ? 'badge-youtube' : 'badge-instagram'}`}>
          {platformLabel}
        </span>
        <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-accent-500/10 text-accent-400 border border-accent-500/20">
          {videoLabel}
        </span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-surface-100 mb-1 line-clamp-2 leading-snug">
        {video.title || 'Untitled'}
      </h3>

      {/* Creator */}
      <div className="flex items-center gap-2 mb-4 text-surface-400 text-sm">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <span className="font-medium text-surface-300">{video.creator}</span>
        {video.follower_count > 0 && (
          <span className="text-surface-500">• {fmt(video.follower_count)} followers</span>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-3 rounded-xl bg-surface-800/60">
          <div className="text-xs text-surface-500 mb-1">Views</div>
          <div className="text-base font-bold text-surface-200">{fmt(video.views)}</div>
        </div>
        <div className="text-center p-3 rounded-xl bg-surface-800/60">
          <div className="text-xs text-surface-500 mb-1">Likes</div>
          <div className="text-base font-bold text-surface-200">{fmt(video.likes)}</div>
        </div>
        <div className="text-center p-3 rounded-xl bg-surface-800/60">
          <div className="text-xs text-surface-500 mb-1">Comments</div>
          <div className="text-base font-bold text-surface-200">{fmt(video.comments)}</div>
        </div>
      </div>

      {/* Engagement Rate */}
      <div className="flex items-center justify-between mb-4 p-3 rounded-xl bg-surface-800/40">
        <span className="text-sm text-surface-400">Engagement Rate</span>
        <span className={`badge border ${engagementColor(video.engagement_rate)}`}>
          {video.engagement_rate}%
        </span>
      </div>

      {/* Meta Row */}
      <div className="flex items-center gap-4 text-xs text-surface-500 mb-4">
        <span className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {video.duration}
        </span>
        <span className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {video.upload_date}
        </span>
      </div>

      {/* Hashtags */}
      {video.hashtags && video.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {video.hashtags.slice(0, 8).map((tag, i) => (
            <span
              key={i}
              className={`px-2 py-0.5 rounded-md text-xs font-medium bg-${platformColor}/5 text-${platformColor}/80 border border-${platformColor}/10`}
              style={{
                backgroundColor: isYouTube ? 'rgba(255,0,51,0.05)' : 'rgba(225,48,108,0.05)',
                color: isYouTube ? 'rgba(255,0,51,0.8)' : 'rgba(225,48,108,0.8)',
                borderColor: isYouTube ? 'rgba(255,0,51,0.15)' : 'rgba(225,48,108,0.15)',
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
