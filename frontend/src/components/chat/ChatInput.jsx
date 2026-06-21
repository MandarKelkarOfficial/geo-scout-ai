import { useState, useRef, useEffect } from 'react';

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
    }
  }, [value]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  return (
    <div className="border-t border-border bg-base px-4 py-4">
      <div className="max-w-3xl mx-auto flex items-end gap-3 bg-surface border border-border rounded-2xl px-4 py-3 focus-within:border-accent transition-colors">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask anything about any place…"
          rows={1}
          className="flex-1 bg-transparent text-sm text-gray-100 placeholder-muted resize-none outline-none leading-relaxed"
          style={{ maxHeight: '160px', overflowY: 'auto' }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="w-9 h-9 rounded-xl bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-all shrink-0"
        >
          {disabled
            ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            : <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
          }
        </button>
      </div>
      <p className="text-center text-xs text-muted mt-2">Enter to send · Shift+Enter for new line</p>
    </div>
  );
}
