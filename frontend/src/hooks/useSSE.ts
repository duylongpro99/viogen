import { useState, useCallback, useRef } from 'react';
import { sendMessageSSE } from '@/lib/api';
import type { SSEEvent, Message } from '@/types';

interface UseSSEReturn {
  messages: Message[];
  streamingMessage: { role: string; name: string; content: string } | null;
  isStreaming: boolean;
  sendMessage: (conversationId: string, content: string) => void;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
}

export function useSSE(): UseSSEReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<{
    role: string;
    name: string;
    content: string;
  } | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<(() => void) | null>(null);

  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const sendMessage = useCallback((conversationId: string, content: string) => {
    // Cancel any existing stream
    if (abortRef.current) {
      abortRef.current();
    }

    setIsStreaming(true);

    // Add user message immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      conversation_id: conversationId,
      role: 'user',
      content,
      metadata: {},
      created_at: new Date().toISOString(),
    };
    addMessage(userMessage);

    abortRef.current = sendMessageSSE(
      conversationId,
      content,
      (event) => {
        try {
          const data: SSEEvent = JSON.parse(event.data);

          switch (data.type) {
            case 'specialist_start':
              setStreamingMessage({
                role: data.role || '',
                name: data.name || '',
                content: '',
              });
              break;

            case 'specialist_chunk':
              setStreamingMessage((prev) => {
                if (!prev) return null;
                return { ...prev, content: prev.content + (data.content || '') };
              });
              break;

            case 'specialist_end':
              // Add completed message
              const specialistMessage: Message = {
                id: crypto.randomUUID(),
                conversation_id: conversationId,
                role: data.role as Message['role'],
                content: data.content || '',
                metadata: { name: data.name },
                created_at: new Date().toISOString(),
              };
              addMessage(specialistMessage);
              setStreamingMessage(null);
              break;

            case 'phase_change':
              // Could emit an event or update state
              console.log('Phase changed to:', data.phase);
              break;
          }
        } catch (e) {
          console.error('Failed to parse SSE event:', e);
        }
      },
      (error) => {
        console.error('SSE error:', error);
        setIsStreaming(false);
        setStreamingMessage(null);
      }
    );

    // Cleanup when all specialists done
    setTimeout(() => {
      setIsStreaming(false);
    }, 30000); // Timeout after 30s
  }, [addMessage]);

  return {
    messages,
    streamingMessage,
    isStreaming,
    sendMessage,
    addMessage,
    setMessages,
  };
}
