export default function Button({ children, variant = 'primary', className = '', ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-accent hover:bg-accent-hover text-white',
    ghost: 'text-muted hover:text-gray-100 hover:bg-surface-hover',
    danger: 'bg-red-800 hover:bg-red-700 text-white',
    outline: 'border border-border text-gray-300 hover:bg-surface-hover',
  };
  return (
    <button className={`${base} ${variants[variant] || variants.primary} ${className}`} {...props}>
      {children}
    </button>
  );
}
