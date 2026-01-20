'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { MessageStream, ChatInput } from '@/components/chat';
import { useSSE } from '@/hooks/useSSE';
import { getSession, createConversation, getMessages } from '@/lib/api';
import type { Session, Conversation } from '@/types';

export default function ChatPage() {
  const params = useParams();
  const sessionId = params.id as string;

  const [session, setSession] = useState<Session | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { messages, streamingMessage, isStreaming, sendMessage, setMessages } = useSSE();

  useEffect(() => {
    async function init() {
      try {
        const sess = await getSession(sessionId);
        setSession(sess);

        // Create a new conversation
        const conv = await createConversation(sessionId);
        setConversation(conv);

        // Load existing messages if any
        const msgs = await getMessages(conv.id);
        setMessages(msgs);
      } catch (e) {
        setError('Failed to initialize chat');
        console.error(e);
      } finally {
        setLoading(false);
      }
    }

    init();
  }, [sessionId, setMessages]);

  const handleSend = (content: string) => {
    if (!conversation) return;
    sendMessage(conversation.id, content);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b px-4 py-3 flex items-center justify-between">
        <h1 className="font-semibold">Creative Studio</h1>
        <span className="text-sm text-gray-500">
          Phase: {conversation?.status || 'ideation'}
        </span>
      </header>

      <MessageStream messages={messages} streamingMessage={streamingMessage} />

      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
