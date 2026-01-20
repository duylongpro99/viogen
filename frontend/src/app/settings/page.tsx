'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ModelSelector } from '@/components/settings/ModelSelector';
import { getSession } from '@/lib/api';
import type { SpecialistRole } from '@/types';

const SPECIALIST_ROLES: SpecialistRole[] = ['style', 'composition', 'story', 'technical', 'critic'];
const DEFAULT_MODELS = ['llama3.2', 'llama3.1', 'mistral', 'phi3', 'gemma2'];

function SettingsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session');

  const [assignments, setAssignments] = useState<Record<string, string>>({
    style: 'llama3.2',
    composition: 'llama3.2',
    story: 'llama3.2',
    technical: 'llama3.2',
    critic: 'llama3.2',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (sessionId) {
      getSession(sessionId).then((session) => {
        if (session.model_assignments) {
          setAssignments({ ...assignments, ...session.model_assignments });
        }
      });
    }
  }, [sessionId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${API_URL}/api/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_assignments: assignments }),
      });
      router.push(`/chat/${sessionId}`);
    } catch (e) {
      console.error('Failed to save:', e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Model Settings</h1>
      <p className="text-gray-600 mb-8">
        Assign Ollama models to each specialist role
      </p>

      <div className="space-y-4 mb-8">
        {SPECIALIST_ROLES.map((role) => (
          <ModelSelector
            key={role}
            role={role}
            value={assignments[role]}
            onChange={(value) => setAssignments({ ...assignments, [role]: value })}
            availableModels={DEFAULT_MODELS}
          />
        ))}
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => router.back()}
          className="px-6 py-2 border rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {saving ? 'Saving...' : 'Save & Continue'}
        </button>
      </div>
    </main>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <SettingsContent />
    </Suspense>
  );
}
