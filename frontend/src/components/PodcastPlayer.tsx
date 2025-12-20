'use client';

import { useState, useEffect, useRef } from 'react';
import { generatePodcast } from '@/lib/api';

interface PodcastPlayerProps {
    sessionId: string;
    isOpen: boolean;
    onClose: () => void;
}

export default function PodcastPlayer({ sessionId, isOpen, onClose }: PodcastPlayerProps) {
    const [loading, setLoading] = useState(false);
    const [script, setScript] = useState('');
    const [title, setTitle] = useState('');
    const [playing, setPlaying] = useState(false);

    // Speech synthesis
    const synthRef = useRef<SpeechSynthesisUtterance | null>(null);

    useEffect(() => {
        if (isOpen && sessionId && !script) {
            loadPodcast();
        }

        return () => {
            // Cleanup
            if (typeof window !== 'undefined') {
                window.speechSynthesis.cancel();
            }
        };
    }, [isOpen, sessionId]);

    const loadPodcast = async () => {
        setLoading(true);
        try {
            const res = await generatePodcast(sessionId);
            setTitle(res.title);
            setScript(res.script);
            // Auto play
            playAudio(res.script);
        } catch (e) {
            alert('Failed to produce podcast. Try again.');
            onClose();
        } finally {
            setLoading(false);
        }
    };

    const playAudio = (text: string) => {
        if (typeof window !== 'undefined') {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.1; // Slightly faster for energy
            utterance.pitch = 1.0;

            utterance.onend = () => setPlaying(false);
            utterance.onstart = () => setPlaying(true);

            synthRef.current = utterance;
            window.speechSynthesis.speak(utterance);
        }
    };

    const togglePlay = () => {
        if (playing) {
            window.speechSynthesis.pause();
            setPlaying(false);
        } else {
            if (window.speechSynthesis.paused) {
                window.speechSynthesis.resume();
                setPlaying(true);
            } else {
                playAudio(script);
            }
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fade-in">
            <div className="bg-[#0f172a] border border-cyan-500/30 rounded-2xl w-full max-w-lg p-8 shadow-2xl relative overflow-hidden bg-gradient-to-b from-[#0f172a] to-cyan-900/20">

                <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white">✕</button>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-12">
                        <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center animate-pulse mb-6">
                            <span className="text-2xl animate-spin">💿</span>
                        </div>
                        <p className="text-cyan-300 font-medium animate-pulse">Recording new episode...</p>
                    </div>
                ) : (
                    <div className="text-center">
                        <div className="mb-8 relative">
                            <div className={`w-32 h-32 mx-auto rounded-full bg-gradient-to-tr from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30 ${playing ? 'animate-pulse' : ''}`}>
                                <span className="text-5xl text-white">🎧</span>
                            </div>
                            {playing && (
                                <div className="absolute -inset-4 border-2 border-cyan-500/20 rounded-full animate-ping"></div>
                            )}
                        </div>

                        <h2 className="text-cyan-400 text-xs font-bold tracking-widest uppercase mb-2">NOW PLAYING</h2>
                        <h3 className="text-2xl font-bold text-white mb-8 line-clamp-2">{title || 'Daily Briefing'}</h3>

                        <div className="flex justify-center items-center gap-6 mb-8">
                            <button
                                onClick={() => {
                                    window.speechSynthesis.cancel();
                                    loadPodcast();
                                }}
                                className="p-3 rounded-full text-slate-400 hover:bg-white/10 transition"
                                title="Regenerate"
                            >
                                🔄
                            </button>

                            <button
                                onClick={togglePlay}
                                className="w-16 h-16 rounded-full bg-white text-black flex items-center justify-center hover:scale-105 transition shadow-xl"
                            >
                                {playing ? '⏸️' : '▶️'}
                            </button>

                            <button
                                onClick={onClose}
                                className="p-3 rounded-full text-slate-400 hover:bg-white/10 transition"
                                title="Stop"
                            >
                                ⏹️
                            </button>
                        </div>

                        <div className="bg-black/30 rounded-xl p-4 h-32 overflow-y-auto text-left text-sm text-slate-400 custom-scrollbar border border-white/5">
                            <p className="whitespace-pre-wrap">{script}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
