'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { crawlWebsite } from '@/lib/api';

import confetti from 'canvas-confetti';

export default function Home() {
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiMode, setAiMode] = useState<'api' | 'local'>('api');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Confetti Explosion!
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.8 },
      colors: ['#00A2FF', '#00B06F', '#FF3B30', '#F5C400']
    });

    setLoading(true);

    try {
      if (!url.trim()) throw new Error('Please enter a URL');
      if (!url.startsWith('http')) throw new Error('URL must start with http:// or https://');

      const response = await crawlWebsite(url, aiMode);

      const params = new URLSearchParams({
        session: response.session_id,
        url: url,
        mode: aiMode,
        title: response.website_title || '',
        links: (response.total_links_found || 0).toString(),
        pages: response.pages_indexed.toString()
      });

      router.push(`/chat?${params.toString()}`);
    } catch (err: any) {
      setError(err.message || 'Failed to process website');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">

      {/* 3D Floating Decor */}
      <div className="absolute top-10 left-10 w-24 h-24 bg-blue-500 rounded-xl shadow-xl animate-float-y border-b-8 border-blue-700 opacity-80 rotate-12"></div>
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-red-500 rounded-xl shadow-xl animate-float-y border-b-8 border-red-700 opacity-80 -rotate-6 [animation-delay:1s]"></div>
      <div className="absolute top-1/2 left-[10%] w-16 h-16 bg-green-500 rounded-lg shadow-xl animate-float-y border-b-4 border-green-700 opacity-60 rotate-45 [animation-delay:2s]"></div>

      <div className="max-w-4xl w-full z-10 grid md:grid-cols-2 gap-12 items-center">

        {/* Left Column: Text */}
        <div className="space-y-6 text-center md:text-left">
          <div className="inline-block px-4 py-2 rounded-full bg-yellow-400 text-yellow-900 border-b-4 border-yellow-600 font-bold text-sm mb-2 rotate-2">
            NEW UPDATE: BLOXY MODE 🧱
          </div>
          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white leading-tight drop-shadow-xl">
            CHAT WITH <br />
            <span className="text-[#00A2FF]">WEBSITES</span>
          </h1>
          <p className="text-xl text-gray-400 font-bold max-w-md mx-auto md:mx-0">
            Turn any boring website into a fun AI character! Just drop the link and press play.
          </p>

          <div className="flex gap-4 justify-center md:justify-start">
            <button onClick={() => router.push('/debate')} className="btn-bloxy btn-bloxy-red px-6 py-3 text-lg">
              ⚔️ Arena
            </button>
            <button className="btn-bloxy btn-bloxy-yellow px-6 py-3 text-lg">
              🏆 Leaderboard
            </button>
          </div>
        </div>

        {/* Right Column: Form Card */}
        <div className="bloxy-card p-8 bg-[#1f2937] border-4 border-[#374151]">
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* AI Mode Selector */}
            <div className="grid grid-cols-2 gap-3 p-2 bg-gray-900 rounded-xl border-2 border-gray-800">
              <button
                type="button"
                onClick={() => setAiMode('api')}
                className={`py-2 px-4 rounded-lg font-bold transition-all ${aiMode === 'api'
                  ? 'bg-blue-500 text-white shadow-lg scale-105'
                  : 'text-gray-500 hover:text-white'
                  }`}
              >
                ⚡ SPEED
              </button>
              <button
                type="button"
                onClick={() => setAiMode('local')}
                className={`py-2 px-4 rounded-lg font-bold transition-all ${aiMode === 'local'
                  ? 'bg-green-500 text-white shadow-lg scale-105'
                  : 'text-gray-500 hover:text-white'
                  }`}
              >
                🔒 SECURE
              </button>
            </div>

            <div className="space-y-2">
              <label htmlFor="url" className="text-sm font-bold text-gray-300 ml-1 uppercase tracking-wider">
                Target URL
              </label>
              <div className="relative group">
                <input
                  id="url"
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://roblox.com"
                  className="bloxy-input pl-4"
                  disabled={loading}
                />
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-red-500/20 border-2 border-red-500 text-red-200 font-bold flex items-center gap-3">
                ⚠️ <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-bloxy btn-bloxy-green text-xl py-4"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin text-2xl">⚙️</span>
                  BUILDING MAP...
                </span>
              ) : (
                '🚀 PLAY NOW'
              )}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
