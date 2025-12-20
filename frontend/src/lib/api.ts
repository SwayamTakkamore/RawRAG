const API_BASE_URL = 'http://localhost:8000/api';

export interface CrawlResponse {
    session_id: string;
    status: string;
    pages_indexed: number;
    website_title?: string;
    total_links_found?: number;
    message: string;
}

export interface ChatResponse {
    answer: string;
    sources: string[];
    confidence: string;
}

export const crawlWebsite = async (url: string, aiMode: 'api' | 'local' = 'api'): Promise<CrawlResponse> => {
    const response = await fetch(`${API_BASE_URL}/crawl?ai_mode=${aiMode}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to crawl website');
    }

    return response.json();
};

export const sendChatMessage = async (
    sessionId: string,
    message: string,
    aiMode: 'api' | 'local' = 'api'
): Promise<ChatResponse> => {
    const response = await fetch(`${API_BASE_URL}/chat?ai_mode=${aiMode}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message,
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to send message');
    }

    return response.json();
};

export interface DebateRequest {
    session_id_1: string;
    session_id_2: string;
    topic: string;
    rounds: number;
}

export interface DebateTurn {
    speaker: string;
    content: string;
}

export interface DebateResponse {
    transcript: DebateTurn[];
    winner: string;
}

export async function startDebate(req: DebateRequest): Promise<DebateResponse> {
    const response = await fetch(`${API_BASE_URL}/debate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(req),
    });

    if (!response.ok) {
        throw new Error('Failed to start debate');
    }

    return response.json();
}

export interface PodcastResponse {
    title: string;
    script: string;
}

export async function generatePodcast(sessionId: string): Promise<PodcastResponse> {
    const response = await fetch(`${API_BASE_URL}/podcast`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: "generate podcast"
        }),
    });

    if (!response.ok) {
        throw new Error('Failed to generate podcast');
    }

    return response.json();
}

export interface DiagramResponse {
    mermaid_code: string;
    description: string;
}

export async function generateDiagram(sessionId: string, prompt?: string): Promise<DiagramResponse> {
    const response = await fetch(`${API_BASE_URL}/diagram`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: prompt || "generate diagram structure"
        }),
    });

    if (!response.ok) {
        throw new Error('Failed to generate diagram');
    }

    return response.json();
}
