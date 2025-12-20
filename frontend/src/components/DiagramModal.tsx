'use client';

import { useState, useEffect, useRef } from 'react';
import { generateDiagram } from '@/lib/api';
import mermaid from 'mermaid';

interface DiagramModalProps {
  sessionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function DiagramModal({ sessionId, isOpen, onClose }: DiagramModalProps) {
  const [loading, setLoading] = useState(false);
  const [code, setCode] = useState('');
  const [desc, setDesc] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      securityLevel: 'loose',
    });
  }, []);

  useEffect(() => {
    if (isOpen && sessionId && !code) {
      loadDiagram();
    }
  }, [isOpen, sessionId]);

  useEffect(() => {
    if (code && containerRef.current) {
      renderMermaid();
    }
  }, [code]);

  const loadDiagram = async () => {
    setLoading(true);
    try {
      const res = await generateDiagram(sessionId, "Visualize the structure and key concepts");
      setCode(res.mermaid_code);
      setDesc(res.description);
    } catch (e) {
      console.error(e);
      setCode('graph TD; A[Error] --> B[Could not generate];');
    } finally {
      setLoading(false);
    }
  };

  const renderMermaid = async () => {
    try {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
        const { svg } = await mermaid.render('mermaid-svg', code);
        containerRef.current.innerHTML = svg;
      }
    } catch (e) {
      console.error("Mermaid Render Error", e);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-[#0f172a] border border-blue-500/30 rounded-2xl w-full max-w-4xl h-[80vh] flex flex-col shadow-2xl relative overflow-hidden">

        {/* Header */}
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-slate-900/50">
          <h2 className="text-blue-400 font-bold flex items-center gap-2">
            <span>📊</span> AI Diagram Generator
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">✕</button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4 flex flex-col items-center justify-center bg-[url('/grid.svg')] bg-repeat opacity-90">
          {loading ? (
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-blue-300 animate-pulse">Analyzing structure...</p>
            </div>
          ) : code.includes('Error') ? (
            <div className="text-red-400 p-4 border border-red-500/30 bg-red-500/10 rounded-lg">
              <h3 className="font-bold mb-2">Generation Failed</h3>
              <p>{desc || "Could not generate diagram."}</p>
              <pre className="mt-2 text-xs bg-black/50 p-2 rounded">{code}</pre>
            </div>
          ) : (
            <div className="w-full h-full flex flex-col items-center">
              <div ref={containerRef} className="mermaid-container w-full flex-1 flex items-center justify-center overflow-auto p-4">
                {/* Mermaid SVG injected here */}
              </div>
              {desc && (
                <div className="mt-4 p-3 bg-black/40 rounded-lg border border-white/5 max-w-2xl text-center">
                  <p className="text-sm text-slate-300">{desc}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Controls */}
        <div className="p-4 border-t border-white/10 flex justify-end gap-3 bg-slate-900/50">
          <button
            onClick={loadDiagram}
            className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 text-sm transition"
          >
            Regenerate
          </button>
        </div>

      </div>
    </div>
  );
}
