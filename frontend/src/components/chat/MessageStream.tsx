import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import type { Message, SpecialistRole } from '@/types';

interface MessageStreamProps {
  messages: Message[];
  streamingMessage?: { role: string; name: string; content: string } | null;
}

export function MessageStream({ messages, streamingMessage }: MessageStreamProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role as SpecialistRole | 'user'}
          name={message.metadata?.name}
          content={message.content}
        />
      ))}
      {streamingMessage && (
        <MessageBubble
          role={streamingMessage.role as SpecialistRole}
          name={streamingMessage.name}
          content={streamingMessage.content}
          isStreaming
        />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
