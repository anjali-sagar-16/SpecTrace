export function Button({
  type = 'button',
  variant = 'primary',
  fullWidth = false,
  loading = false,
  disabled = false,
  onClick,
  children,
  className = '',
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant} ${fullWidth ? 'btn-full' : ''} ${className}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && (
        <span className="btn-spinner" aria-hidden="true" />
      )}
      <span className="btn-label">{children}</span>
    </button>
  );
}
