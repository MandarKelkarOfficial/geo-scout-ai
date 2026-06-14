const ICONS = { geocoding: '📍', weather: '🌤', places: '🏙', satellite: '🛰', real_estate: '🏠', rag: '📚' };

export default function ToolsBadge({ tools = [] }) {
  if (!tools.length) return null;
  return (
    <div className="flex flex-wrap gap-1.5 mt-2">
      {tools.map(tool => (
        <span key={tool} className="inline-flex items-center gap-1 text-xs bg-[#1e2a1e] text-green-400 border border-green-900 px-2 py-0.5 rounded-full">
          <span>{ICONS[tool] || '⚙'}</span>
          <span>{tool.replace(/_/g, ' ')}</span>
        </span>
      ))}
    </div>
  );
}
