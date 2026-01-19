'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createSession } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    try {
      // Create session with default model assignments
      const session = await createSession({
        style: 'llama3.2',
        composition: 'llama3.2',
        story: 'llama3.2',
        technical: 'llama3.2',
        critic: 'llama3.2',
      });
      router.push(`/chat/${session.id}`);
    } catch (e) {
      console.error('Failed to create session:', e);
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Creative Studio</h1>
      <p className="text-gray-600 mb-8 text-center max-w-md">
        Collaborate with AI specialists to create images and videos.
        Watch Luna, Frame, Saga, Pixel, and Lens work together on your vision.
      </p>
      <button
        onClick={handleStart}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
      >
        {loading ? 'Creating session...' : 'Start Creating'}
      </button>
    </main>
  );
}
