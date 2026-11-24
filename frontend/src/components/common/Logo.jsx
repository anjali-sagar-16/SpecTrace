export function Logo({ size = 'medium', showTagline = false }) {
  const iconSize = size === 'large' ? 32 : size === 'small' ? 22 : 26;

  return (
    <div className={`brand-logo brand-logo--${size}`}>
      <div className="brand-icon" aria-hidden="true">
        <svg
          width={iconSize}
          height={iconSize}
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Base badge */}
          <rect width="32" height="32" rx="7" fill="#0f172a" />
          
          {/* SpecTrace dependency trace paths */}
          <path
            d="M9 16C13 16 16 9 23 9"
            stroke="#60a5fa"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
          <path
            d="M9 16C13 16 16 23 23 23"
            stroke="#60a5fa"
            strokeWidth="2.2"
            strokeLinecap="round"
          />

          {/* Trace Nodes */}
          <circle cx="9" cy="16" r="3" fill="#2563eb" stroke="#ffffff" strokeWidth="1.5" />
          <circle cx="23" cy="9" r="2.5" fill="#38bdf8" />
          <circle cx="23" cy="23" r="2.5" fill="#38bdf8" />
          
          {/* AI Trace Evaluation Core */}
          <circle cx="16" cy="16" r="1.75" fill="#ffffff" />
        </svg>
      </div>

      <div className="brand-meta">
        <span className="brand-name">SpecTrace</span>
        {showTagline && (
          <span className="brand-tag">Change Intelligence</span>
        )}
      </div>
    </div>
  );
}
