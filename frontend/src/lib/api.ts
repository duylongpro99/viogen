import type { Session, Conversation, Message } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function createSession(modelAssignments: Record<string, string> = {}): Promise<Session> {
  const res = await fetch(`${API_URL}/api/sessions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_assignments: modelAssignments, settings: {} }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function getSession(sessionId: string): Promise<Session> {
  const res = await fetch(`${API_URL}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get session');
  return res.json();
}

export async function createConversation(sessionId: string): Promise<Conversation> {
  const res = await fetch(`${API_URL}/api/chat/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  const res = await fetch(`${API_URL}/api/chat/conversations/${conversationId}/messages`);
  if (!res.ok) throw new Error('Failed to get messages');
  return res.json();
}

export function sendMessageSSE(
  conversationId: string,
  content: string,
  onEvent: (event: MessageEvent) => void,
  onError: (error: Event) => void,
): () => void {
  // First POST the message, which returns SSE
  const controller = new AbortController();

  fetch(`${API_URL}/api/chat/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
    signal: controller.signal,
  }).then(async (res) => {
    if (!res.ok || !res.body) {
      onError(new Event('error'));
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          onEvent(new MessageEvent('message', { data }));
        }
      }
    }
  }).catch((err) => {
    if (err.name !== 'AbortError') {
      onError(new Event('error'));
    }
  });

  return () => controller.abort();
}
