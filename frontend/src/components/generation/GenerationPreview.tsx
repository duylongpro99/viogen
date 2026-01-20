'use client';

import { useState, useEffect } from 'react';
import { ProgressBar } from './ProgressBar';

interface Generation {
  id: string;
  status: 'queued' | 'running' | 'complete' | 'failed';
  progress: number;
  parameters?: {
    prompt_id?: string;
    images?: Array<{ filename: string; subfolder: string }>;
  };
  error?: string;
}

interface GenerationPreviewProps {
  conversationId: string;
}

export function GenerationPreview({ conversationId }: GenerationPreviewProps) {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGenerations = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/generations/conversation/${conversationId}`);
        if (res.ok) {
          setGenerations(await res.json());
        }
      } catch (e) {
        console.error('Failed to fetch generations:', e);
      } finally {
        setLoading(false);
      }
    };

    fetchGenerations();

    // Poll for updates
    const interval = setInterval(fetchGenerations, 2000);
    return () => clearInterval(interval);
  }, [conversationId]);

  if (loading) {
    return <div className="p-4 text-gray-500">Loading generations...</div>;
  }

  if (generations.length === 0) {
    return null;
  }

  return (
    <div className="border-t p-4 space-y-4">
      <h3 className="font-medium">Generations</h3>
      {generations.map((gen) => (
        <div key={gen.id} className="border rounded-lg p-4">
          {gen.status === 'running' || gen.status === 'queued' ? (
            <ProgressBar progress={gen.progress} status={gen.status} />
          ) : gen.status === 'failed' ? (
            <div className="text-red-500">Failed: {gen.error}</div>
          ) : gen.status === 'complete' ? (
            <div className="text-green-600">Complete! Check ComfyUI output folder.</div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
