'use client';

import { useState } from 'react';
import { crawlWebsite, startDebate, CrawlResponse, DebateResponse } from '@/lib/api';

export default function DebatePage() {
    const [url1, setUrl1] = useState('');
    const [url2, setUrl2] = useState('');
    const [topic, setTopic] = useState('Which is better?');

    const [session1, setSession1] = useState<string | null>(null);
    const [session2, setSession2] = useState<string | null>(null);

    const [loading1, setLoading1] = useState(false);
    const [loading2, setLoading2] = useState(false);
    const [debating, setDebating] = useState(false);

    const [debateResult, setDebateResult] = useState<DebateResponse | null>(null);

    const handleCrawl1 = async () => {
        setLoading1(true);
        try {
            const res = await crawlWebsite(url1);
            setSession1(res.session_id);
        } catch (e) {
            alert('Failed to crawl URL 1');
        } finally {
            setLoading1(false);
        }
    };

    const handleCrawl2 = async () => {
        setLoading2(true);
        try {
            const res = await crawlWebsite(url2);
            setSession2(res.session_id);
        } catch (e) {
            alert('Failed to crawl URL 2');
        } finally {
            setLoading2(false);
        }
    };

    const startTheBattle = async () => {
        if (!session1 || !session2) return;
        setDebating(true);
        try {
            const res = await startDebate({
                session_id_1: session1,
                session_id_2: session2,
                topic: topic,
                rounds: 3
            });
            setDebateResult(res);
        } catch (e) {
            alert('Debate failed to start');
        } finally {
            setDebating(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-white p-8">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-4xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-orange-400 to-red-600">
                    ⚔️ AI Debate Arena ⚔️
                </h1>

                {/* Setup Phase */}
                <div className="grid md:grid-cols-2 gap-8 mb-12">
                    {/* Contender 1 */}
                    <div className="glass-panel p-6 rounded-2xl border border-blue-500/30 bg-blue-900/10">
                        <h2 className="text-xl font-bold text-blue-400 mb-4">Contender A</h2>
                        <div className="flex gap-2 mb-4">
                            <input
                                value={url1}
                                onChange={(e) => setUrl1(e.target.value)}
                                placeholder="https://apple.com"
                                className="flex-1 bg-black/30 border border-blue-500/30 rounded p-2 text-sm"
                            />
                            <button
                                onClick={handleCrawl1}
                                disabled={loading1 || !!session1}
                                className="bg-blue-600 hover:bg-blue-500 px-4 rounded text-sm font-bold disabled:opacity-50"
                            >
                                {loading1 ? 'Loading...' : session1 ? 'READY' : 'PREP'}
                            </button>
                        </div>
                        {session1 && <div className="text-green-400 text-xs text-center">✅ Knowledge Loaded</div>}
                    </div>

                    {/* Contender 2 */}
                    <div className="glass-panel p-6 rounded-2xl border border-red-500/30 bg-red-900/10">
                        <h2 className="text-xl font-bold text-red-400 mb-4">Contender B</h2>
                        <div className="flex gap-2 mb-4">
                            <input
                                value={url2}
                                onChange={(e) => setUrl2(e.target.value)}
                                placeholder="https://samsung.com"
                                className="flex-1 bg-black/30 border border-red-500/30 rounded p-2 text-sm"
                            />
                            <button
                                onClick={handleCrawl2}
                                disabled={loading2 || !!session2}
                                className="bg-red-600 hover:bg-red-500 px-4 rounded text-sm font-bold disabled:opacity-50"
                            >
                                {loading2 ? 'Loading...' : session2 ? 'READY' : 'PREP'}
                            </button>
                        </div>
                        {session2 && <div className="text-green-400 text-xs text-center">✅ Knowledge Loaded</div>}
                    </div>
                </div>

                {/* Action Button */}
                <div className="text-center mb-12">
                    <input
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="Enter debate topic..."
                        className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 w-full max-w-md mb-4 text-center"
                    />
                    <br />
                    <button
                        onClick={startTheBattle}
                        disabled={!session1 || !session2 || debating}
                        className="bg-gradient-to-r from-orange-500 to-red-600 text-white px-8 py-4 rounded-xl text-xl font-bold shadow-lg hover:scale-105 transition disabled:opacity-50 disabled:grayscale"
                    >
                        {debating ? '🔥 THOUGHTS ARE CLASHING... 🔥' : 'FIGHT! 🔔'}
                    </button>
                </div>

                {/* The Debate Transcript */}
                {debateResult && (
                    <div className="space-y-6 max-w-4xl mx-auto pb-20">
                        {debateResult.transcript.map((turn, i) => (
                            <div key={i} className={`flex ${turn.speaker === 'Agent A' ? 'justify-start' : 'justify-end'}`}>
                                <div className={`max-w-[80%] rounded-2xl p-6 ${turn.speaker === 'Agent A'
                                    ? 'bg-blue-900/20 border border-blue-500/30 text-blue-100 rounded-bl-none'
                                    : 'bg-red-900/20 border border-red-500/30 text-red-100 rounded-br-none'
                                    }`}>
                                    <div className="text-xs font-bold mb-2 opacity-50 uppercase tracking-widest">
                                        {turn.speaker === 'Agent A' ? `🔵 ${url1}` : `🔴 ${url2}`}
                                    </div>
                                    <p className="whitespace-pre-wrap">{turn.content}</p>
                                </div>
                            </div>
                        ))}

                        <div className="mt-12 p-8 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-2xl text-center">
                            <h3 className="text-2xl font-bold text-yellow-500 mb-4">🏆 VERDICT</h3>
                            <p className="text-xl">{debateResult.winner}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
