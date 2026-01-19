export interface Session {
  id: string;
  created_at: string;
  model_assignments: Record<string, string>;
  settings: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  session_id: string;
  status: 'ideation' | 'refinement' | 'synthesis' | 'review' | 'generating' | 'complete';
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'style' | 'composition' | 'story' | 'technical' | 'critic' | 'system';
  content: string;
  metadata: {
    name?: string;
  };
  created_at: string;
}

export interface SSEEvent {
  type: 'user_message' | 'specialist_start' | 'specialist_chunk' | 'specialist_end' | 'phase_change';
  role?: string;
  name?: string;
  content?: string;
  phase?: string;
}

export type SpecialistRole = 'style' | 'composition' | 'story' | 'technical' | 'critic';

export const SPECIALIST_INFO: Record<SpecialistRole, { name: string; color: string; icon: string }> = {
  style: { name: 'Luna', color: 'purple', icon: '🎨' },
  composition: { name: 'Frame', color: 'blue', icon: '📐' },
  story: { name: 'Saga', color: 'amber', icon: '📖' },
  technical: { name: 'Pixel', color: 'green', icon: '⚙️' },
  critic: { name: 'Lens', color: 'red', icon: '🔍' },
};
