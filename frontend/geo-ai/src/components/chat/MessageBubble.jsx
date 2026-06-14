import ToolsBadge from './ToolsBadge';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} px-4 py-1.5`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-accent flex items-center justify-center text-xs font-bold mr-2 mt-1 shrink-0">G</div>
      )}
      <div className={`max-w-[75%] ${isUser ? 'max-w-[60%]' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-user-bubble text-blue-100 rounded-tr-sm'
              : 'bg-surface border-l-2 border-accent text-gray-200 rounded-tl-sm'
          }`}
        >
          {message.content.split('\n').map((line, i) => (
            <span key={i}>{line}{i < message.content.split('\n').length - 1 && <br />}</span>
          ))}
        </div>
        {!isUser && <ToolsBadge tools={message.tools_used} />}
      </div>
    </div>
  );
}
