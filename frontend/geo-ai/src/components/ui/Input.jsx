export default function Input({ label, error, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-xs text-muted font-medium uppercase tracking-wide">{label}</label>}
      <input
        className={`bg-surface border ${error ? 'border-red-600' : 'border-border'} text-gray-100 rounded-xl px-4 py-2.5 text-sm placeholder-muted focus:outline-none focus:border-accent transition-colors ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  );
}
