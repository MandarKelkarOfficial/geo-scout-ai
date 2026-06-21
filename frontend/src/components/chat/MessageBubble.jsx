import ToolsBadge from './ToolsBadge';

/**
 * Renders a single inline text segment, parsing **bold** and `code` spans.
 */
function InlineText({ text }) {
  // Split on **bold** and `code` patterns
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i} className="font-semibold text-gray-100">{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith('`') && part.endsWith('`')) {
          return (
            <code key={i} className="bg-black/30 text-amber-300 text-xs font-mono px-1.5 py-0.5 rounded">
              {part.slice(1, -1)}
            </code>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

/**
 * Renders a full message content string as structured rich text.
 * Supports: ## headers, numbered lists, bullet lists, blank line spacing, inline bold/code.
 */
function RichText({ content }) {
  const lines = content.split('\n');
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Empty line → small vertical gap
    if (line.trim() === '') {
      elements.push(<div key={i} className="h-2" />);
      i++;
      continue;
    }

    // ## Header
    if (line.startsWith('## ')) {
      elements.push(
        <p key={i} className="text-base font-bold text-gray-100 mt-1 mb-1">
          <InlineText text={line.slice(3)} />
        </p>
      );
      i++;
      continue;
    }

    // # Header (title-level)
    if (line.startsWith('# ')) {
      elements.push(
        <p key={i} className="text-lg font-bold text-gray-100 mt-1 mb-1">
          <InlineText text={line.slice(2)} />
        </p>
      );
      i++;
      continue;
    }

    // Numbered list item: "1. ...", "2. ..."
    if (/^\d+\.\s/.test(line)) {
      const listItems = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        const text = lines[i].replace(/^\d+\.\s/, '');
        const subLines = text.split('\\n');
        listItems.push(
          <li key={i} className="mb-1.5 leading-snug">
            <InlineText text={subLines[0]} />
            {subLines.slice(1).map((sl, si) => (
              <div key={si} className="text-muted text-xs mt-0.5 ml-1">
                <InlineText text={sl} />
              </div>
            ))}
          </li>
        );
        i++;
        // Sub-lines indented under a list item (e.g. "   📍 address")
        while (i < lines.length && lines[i].startsWith('   ')) {
          listItems[listItems.length - 1] = (
            <li key={`${i}-main`} className="mb-1.5 leading-snug">
              <InlineText text={lines[i - 1].replace(/^\d+\.\s/, '')} />
              <div className="text-muted text-xs mt-0.5 ml-1">
                <InlineText text={lines[i].trim()} />
              </div>
            </li>
          );
          i++;
        }
      }
      elements.push(
        <ol key={`ol-${i}`} className="list-decimal list-inside space-y-1 my-1 text-gray-300">
          {listItems}
        </ol>
      );
      continue;
    }

    // Bullet list item: "- ..." or "• ..."
    if (line.startsWith('- ') || line.startsWith('• ')) {
      const listItems = [];
      while (i < lines.length && (lines[i].startsWith('- ') || lines[i].startsWith('• '))) {
        const text = lines[i].slice(2);
        listItems.push(
          <li key={i} className="mb-1">
            <InlineText text={text} />
          </li>
        );
        i++;
      }
      elements.push(
        <ul key={`ul-${i}`} className="list-disc list-inside space-y-1 my-1 text-gray-300">
          {listItems}
        </ul>
      );
      continue;
    }

    // Indented sub-line (e.g. "   📍 something")
    if (line.startsWith('   ')) {
      elements.push(
        <div key={i} className="text-muted text-xs ml-4 -mt-1 mb-1">
          <InlineText text={line.trim()} />
        </div>
      );
      i++;
      continue;
    }

    // Normal paragraph line
    elements.push(
      <p key={i} className="leading-relaxed">
        <InlineText text={line} />
      </p>
    );
    i++;
  }

  return <div className="space-y-0.5">{elements}</div>;
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} px-4 py-1.5`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-accent flex items-center justify-center text-xs font-bold mr-2 mt-1 shrink-0 select-none">
          G
        </div>
      )}
      <div className={`max-w-[75%] ${isUser ? 'max-w-[60%]' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm ${
            isUser
              ? 'bg-user-bubble text-blue-100 rounded-tr-sm'
              : 'bg-surface border-l-2 border-accent text-gray-300 rounded-tl-sm'
          }`}
        >
          {isUser
            ? <span className="leading-relaxed">{message.content}</span>
            : <RichText content={message.content} />
          }
        </div>
        {!isUser && <ToolsBadge tools={message.tools_used} />}
      </div>
    </div>
  );
}
