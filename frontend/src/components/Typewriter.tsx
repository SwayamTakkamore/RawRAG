'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface TypewriterProps {
    content: string;
    speed?: number;
    onComplete?: () => void;
}

export default function Typewriter({ content, speed = 10, onComplete }: TypewriterProps) {
    const [displayedContent, setDisplayedContent] = useState('');
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        if (currentIndex < content.length) {
            const timeout = setTimeout(() => {
                setDisplayedContent(prev => prev + content[currentIndex]);
                setCurrentIndex(prev => prev + 1);
            }, speed);

            return () => clearTimeout(timeout);
        } else {
            if (onComplete) onComplete();
        }
    }, [currentIndex, content, speed, onComplete]);

    // If content changes drastically (new message), reset
    useEffect(() => {
        if (!content.startsWith(displayedContent) && displayedContent !== '') {
            setDisplayedContent('');
            setCurrentIndex(0);
        }
    }, [content]);

    return (
        <div className="prose prose-invert max-w-none text-base font-medium">
            <ReactMarkdown>{displayedContent}</ReactMarkdown>
            {currentIndex < content.length && (
                <span className="inline-block w-2 h-4 bg-white animate-pulse ml-1 align-middle"></span>
            )}
        </div>
    );
}
