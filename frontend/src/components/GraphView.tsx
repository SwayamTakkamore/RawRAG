'use client';

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import for ForceGraph3D to avoid SSR issues
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), { ssr: false });

interface GraphNode {
    id: string;
    name: string;
    val: number;
}

interface GraphLink {
    source: string;
    target: string;
}

interface GraphData {
    nodes: GraphNode[];
    links: GraphLink[];
}

interface GraphViewProps {
    sessionId: string;
    onClose: () => void;
}

export default function GraphView({ sessionId, onClose }: GraphViewProps) {
    const [data, setData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState(true);
    const fgRef = useRef<any>(null);

    useEffect(() => {
        // Fetch graph data
        const fetchGraph = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/graph/${sessionId}`);
                if (!res.ok) throw new Error('Failed to load graph');
                const graphData = await res.json();

                // Add random size variation for visual appeal
                const nodes = graphData.nodes.map((n: any) => ({
                    ...n,
                    val: Math.random() * 5 + 1 // random size
                }));

                setData({ ...graphData, nodes });
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchGraph();
    }, [sessionId]);

    return (
        <div className="fixed inset-0 z-[100] bg-black/90 flex flex-col items-center justify-center">
            {/* Header */}
            <div className="absolute top-4 right-4 z-[110]">
                <button
                    onClick={onClose}
                    className="bg-white/10 hover:bg-white/20 text-white rounded-full p-3 transition backdrop-blur-md"
                >
                    ✕
                </button>
            </div>

            <div className="absolute top-4 left-4 z-[110] text-white">
                <h2 className="text-xl font-bold">Knowledge Graph 🌌</h2>
                <p className="text-xs text-slate-400">
                    Showing {data?.nodes.length || 0} pages and {data?.links.length || 0} connections
                </p>
            </div>

            {loading ? (
                <div className="text-white animate-pulse">Loading Galaxy...</div>
            ) : (
                <div className="w-full h-full">
                    {data && (
                        <ForceGraph3D
                            ref={fgRef}
                            graphData={data}
                            nodeLabel="name"
                            nodeColor={() => '#60a5fa'}
                            linkColor={() => 'rgba(255,255,255,0.2)'}
                            nodeRelSize={4}
                            linkDirectionalParticles={2}
                            linkDirectionalParticleSpeed={0.005}
                            backgroundColor="#000000"
                            onNodeClick={(node: any) => {
                                // Focus camera on node
                                const distance = 40;
                                const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

                                fgRef.current.cameraPosition(
                                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
                                    node, // lookAt ({ x, y, z })
                                    3000  // ms transition duration
                                );
                            }}
                        />
                    )}
                </div>
            )}
        </div>
    );
}
