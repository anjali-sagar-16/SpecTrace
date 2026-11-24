export function Alert({ type = 'info', title, children, onClose }) {
  return (
    <div className={`alert-box alert-${type}`} role="status">
      <div className="alert-body">
        {title && <strong className="alert-title">{title}</strong>}
        <div className="alert-message">{children}</div>
      </div>
      {onClose && (
        <button
          type="button"
          className="alert-dismiss-btn"
          onClick={onClose}
          aria-label="Dismiss notice"
        >
          &times;
        </button>
      )}
    </div>
  );
}
