'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function VoiceControl({ latestMessage }: { latestMessage?: string }) {
    const router = useRouter();
    const [listening, setListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [feedback, setFeedback] = useState('');

    // Recognition ref
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        if (typeof window !== 'undefined') {
            // @ts-ignore
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onstart = () => {
                    setListening(true);
                    setFeedback('Listening... (Say "Scroll Down" or "Go Home")');
                };

                recognition.onend = () => {
                    setListening(false);
                    // Auto restart if intended? For now, manual toggle is safer for demo.
                };

                recognition.onresult = (event: any) => {
                    const current = event.resultIndex;
                    const transcriptText = event.results[current][0].transcript.toLowerCase().trim();
                    setTranscript(transcriptText);
                    handleCommand(transcriptText);
                };

                recognitionRef.current = recognition;
            }
        }
    }, [latestMessage]);

    const handleCommand = (cmd: string) => {
        const container = document.getElementById('chat-container');

        if (cmd.includes('scroll down')) {
            let scrolled = false;
            if (container) {
                container.scrollBy({ top: 300, behavior: 'smooth' });
                scrolled = true;
            }
            // Also try window scroll for main page
            window.scrollBy({ top: 300, behavior: 'smooth' });
            setFeedback(scrolled ? '⬇️ Scrolling chat...' : '⬇️ Scrolling page...');

        } else if (cmd.includes('scroll up')) {
            let scrolled = false;
            if (container) {
                container.scrollBy({ top: -300, behavior: 'smooth' });
                scrolled = true;
            }
            window.scrollBy({ top: -300, behavior: 'smooth' });
            setFeedback(scrolled ? '⬆️ Scrolling chat...' : '⬆️ Scrolling page...');

        } else if (cmd.includes('bottom') || cmd.includes('end')) {
            if (container) {
                container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
                setFeedback('⬇️ Jumping to bottom');
            }
        } else if (cmd.includes('go home') || cmd.includes('end chat')) {
            router.push('/');
            setFeedback('🏠 Going home');
        } else if (cmd.includes('read') || cmd.includes('speak')) {
            if (latestMessage) {
                setFeedback('🗣️ Speaking...');
                const utterance = new SpeechSynthesisUtterance(latestMessage);
                window.speechSynthesis.speak(utterance);
            } else {
                setFeedback('❌ Nothing to read');
            }
        } else if (cmd.includes('stop')) {
            window.speechSynthesis.cancel();
            setFeedback('🛑 Stopped');
        } else {
            setFeedback(`❓ Unknown: "${cmd}"`);
        }
    };

    const toggleListen = () => {
        if (listening) {
            recognitionRef.current?.stop();
        } else {
            recognitionRef.current?.start();
        }
    };

    if (typeof window !== 'undefined' && !('webkitSpeechRecognition' in window)) {
        return null; // Not supported
    }

    return (
        <div className="fixed bottom-24 right-8 z-50 flex flex-col items-end gap-2">
            {/* Feedback Bubble */}
            {feedback && listening && (
                <div className="bg-black/80 text-cyan-400 px-4 py-2 rounded-xl backdrop-blur border border-cyan-500/30 animate-fade-in mb-2 shadow-lg shadow-cyan-500/20">
                    {feedback}
                </div>
            )}

            {/* Mic Button */}
            <button
                onClick={toggleListen}
                className={`w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all hover:scale-110 ${listening
                    ? 'bg-red-500 animate-pulse ring-4 ring-red-500/30'
                    : 'bg-cyan-600 hover:bg-cyan-500 ring-2 ring-cyan-400/50'
                    }`}
            >
                <span className="text-2xl">{listening ? '🎙️' : '🔇'}</span>
            </button>
        </div>
    );
}
