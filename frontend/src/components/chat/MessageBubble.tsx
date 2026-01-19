import { SpecialistAvatar } from './SpecialistAvatar';
import { SPECIALIST_INFO, type SpecialistRole } from '@/types';

interface MessageBubbleProps {
  role: SpecialistRole | 'user' | 'system';
  name?: string;
  content: string;
  isStreaming?: boolean;
}

export function MessageBubble({ role, name, content, isStreaming }: MessageBubbleProps) {
  const isUser = role === 'user';
  const displayName = isUser ? 'You' : name || SPECIALIST_INFO[role as SpecialistRole]?.name || role;

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <SpecialistAvatar role={role as SpecialistRole | 'user'} />
      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        <div className="text-xs text-gray-500 mb-1">{displayName}</div>
        <div
          className={`inline-block rounded-lg px-4 py-2 max-w-[80%] ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
          )}
        </div>
      </div>
    </div>
  );
}
