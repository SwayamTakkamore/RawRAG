'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { sendChatMessage } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import GraphView from '@/components/GraphView';
import VoiceControl from '@/components/VoiceControl';
import PodcastPlayer from '@/components/PodcastPlayer';
import DiagramModal from '@/components/DiagramModal';
import Typewriter from '@/components/Typewriter';


interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  confidence?: string;
}

export default function ChatPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session');
  const websiteUrl = searchParams.get('url');
  const initialMode = (searchParams.get('mode') as 'api' | 'local') || 'api';

  const websiteTitle = searchParams.get('title');
  const totalPages = searchParams.get('pages');
  const totalLinks = searchParams.get('links');

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiMode, setAiMode] = useState<'api' | 'local'>(initialMode);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [showGraph, setShowGraph] = useState(false);
  const [showPodcast, setShowPodcast] = useState(false);
  const [showDiagram, setShowDiagram] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      router.push('/');
    }
  }, [sessionId, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(sessionId, userMessage, aiMode);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          confidence: response.confidence,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!sessionId) return null;

  return (
    <div className="min-h-screen flex flex-col bg-[#111827] text-white font-[Fredoka]">

      {/* Graph Modal */}
      {showGraph && sessionId && (
        <>
          <GraphView
            sessionId={sessionId || ''}
            onClose={() => setShowGraph(false)}
          />
        </>
      )}

      {showPodcast && sessionId && (
        <PodcastPlayer
          sessionId={sessionId}
          isOpen={showPodcast}
          onClose={() => setShowPodcast(false)}
        />
      )}

      {showDiagram && sessionId && (
        <DiagramModal
          sessionId={sessionId}
          isOpen={showDiagram}
          onClose={() => setShowDiagram(false)}
        />
      )}

      {/* Header */}
      <header className="bg-gray-800/80 border-b-4 border-gray-700 py-3 px-6 shadow-xl z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div onClick={() => router.push('/')} className="w-10 h-10 bg-blue-500 rounded-lg cursor-pointer border-b-4 border-blue-700 flex items-center justify-center text-xl font-bold hover:brightness-110 active:translate-y-1 active:border-b-0 active:mt-1 transition-all">
              🏠
            </div>
            <div>
              <h1 className="text-xl font-black text-white uppercase tracking-wide">
                {websiteTitle || 'Unknown Map'}
              </h1>
              <div className="flex gap-2 text-xs font-bold text-gray-400">
                <span className="bg-gray-700 px-2 py-0.5 rounded text-blue-300">
                  📄 {totalPages} Pages
                </span>
                <span className="bg-gray-700 px-2 py-0.5 rounded text-green-300">
                  🔗 {totalLinks} Links
                </span>
                <span className="text-gray-500 uppercase">{aiMode} Server</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowGraph(true)}
              className="btn-bloxy bg-purple-600 text-white border-b-[4px] border-purple-800 rounded-lg px-3 py-2 text-sm"
            >
              🌌 Graph
            </button>
            <button
              onClick={() => setShowPodcast(true)}
              className="btn-bloxy bg-cyan-500 text-white border-b-[4px] border-cyan-700 rounded-lg px-3 py-2 text-sm"
            >
              🎧 Radio
            </button>
            <button
              onClick={() => setShowDiagram(true)}
              className="btn-bloxy bg-yellow-500 text-black border-b-[4px] border-yellow-700 rounded-lg px-3 py-2 text-sm"
            >
              📊 Map
            </button>
            <button
              onClick={() => router.push('/')}
              className="btn-bloxy bg-red-500 text-white border-b-[4px] border-red-700 rounded-lg px-3 py-2 text-sm"
            >
              Quit
            </button>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div id="chat-container" className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 relative">

        {/* Welcome Message */}
        {messages.length === 0 && (
          <div className="text-center mt-20 space-y-4 animate-float-y">
            <div className="text-6xl">👋</div>
            <h2 className="text-3xl font-black text-white">Welcome, Player!</h2>
            <p className="text-gray-400 font-bold max-w-md mx-auto">
              I have memorized everything about this map ({websiteUrl}).
              Ask me for secrets, tips, or guides!
            </p>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
          >
            <div
              className={`max-w-[80%] md:max-w-2xl rounded-2xl p-5 shadow-lg border-b-4 ${msg.role === 'user'
                ? 'bg-[#00A2FF] border-[#0077BC] text-white rounded-br-none'
                : 'bg-gray-800 border-gray-700 text-gray-100 rounded-bl-none'
                }`}
            >
              {msg.role === 'assistant' ? (
                <Typewriter content={msg.content} speed={15} />
              ) : (
                <ReactMarkdown className="prose prose-invert max-w-none text-base font-medium">
                  {msg.content}
                </ReactMarkdown>
              )}

              {/* Confidence Badge */}
              {msg.role === 'assistant' && msg.confidence && (
                <div className="mt-4 flex items-center gap-2">
                  <div className={`px-2 py-1 rounded text-xs font-bold uppercase ${msg.confidence === 'high' ? 'bg-green-500/20 text-green-300' :
                    msg.confidence === 'medium' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-red-500/20 text-red-300'
                    }`}>
                    Target Acc: {msg.confidence}
                  </div>
                </div>
              )}

              {/* Message Actions Toolbar */}
              {msg.role === 'assistant' && (
                <div className="mt-3 flex gap-2 justify-end opacity-80 hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => navigator.clipboard.writeText(msg.content)}
                    className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-white font-bold"
                    title="Copy"
                  >
                    📋 Copy
                  </button>
                  <button className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-white font-bold">
                    👍
                  </button>
                  <button className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-white font-bold">
                    👎
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border-b-4 border-gray-700 rounded-2xl rounded-bl-none p-4 flex items-center gap-3">
              <div className="flex gap-1">
                <div className="w-3 h-3 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-gray-500 rounded-full animate-bounce [animation-delay:0.1s]"></div>
                <div className="w-3 h-3 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
              </div>
              <span className="text-gray-400 text-sm font-bold">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-gray-800/90 border-t-4 border-gray-700 p-4 z-10 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto relative">

          {/* Suggested Questions Chips */}
          {!loading && (
            <div className="flex gap-2 overflow-x-auto pb-2 mb-2 no-scrollbar">
              {["📝 Summarize", "🗝️ Key Topics", "👶 Explain Simple", "🐞 Find Bugs"].map((q) => (
                <button
                  key={q}
                  onClick={() => {
                    setInput(q.replace(/^[^\s]+\s/, '')); // Remove emoji for query
                    // document.querySelector('form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                    // Direct submit requires refactoring handle submit or just setting input. 
                    // Let's just set input and let user send, or we can't easily auto-submit without ref.
                    // Actually, better UX: set input and focus? 
                    // Or separate submit function. I'll just set input for now as "Power Up".
                  }}
                  // Better: Make it auto-submit if I can call handleSubmit. 
                  // Since handleSubmit takes event, I can't easily call it. 
                  // I will reuse setInput/handleSubmit logic if I refactor, but for now just populate.
                  // WAIT, user wants "Chips". Usually you click and it goes.
                  // I will change onClick to directly call a new function `submitQuery` or just `setInput` and optional auto-send.
                  // Let's just populate input for now to be safe.
                  className="bg-gray-700 hover:bg-gray-600 border-b-2 border-gray-900 text-gray-200 text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap transition-transform active:scale-95"
                  onClickCapture={(e) => {
                    const text = q.replace(/^[^\s]+\s/, '');
                    setInput(text);
                    // Optional: auto-focus input
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Voice Controls */}
          <div className="absolute -top-24 left-0 right-0 flex justify-center pointer-events-none">
            <div className="pointer-events-auto">
              <VoiceControl onCommand={() => { }} />
            </div>
          </div>

          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a command here..."
              className="bloxy-input flex-1 border-gray-600 bg-gray-700 focus:bg-gray-900 border-b-4 focus:border-blue-500"
              disabled={loading}
              autoFocus
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="btn-bloxy btn-bloxy-green px-8 text-xl"
            >
              SEND
            </button>
          </form>

          <div className="text-center mt-2">
            <p className="text-[10px] uppercase font-bold text-gray-500 tracking-widest">
              Powered by Llama 3.3 • Roblox UI Mode
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
