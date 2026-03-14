/**
 * ResearchHub AI – Paper Q&A Component
 * Chat-style interface for asking questions about a specific paper.
 */

import React, { useState, useEffect, useRef } from 'react';
import { listPapers, askQuestion } from '../api';

export default function PaperQA() {
    const [papers, setPapers] = useState([]);
    const [selectedPaperId, setSelectedPaperId] = useState('');
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingPapers, setLoadingPapers] = useState(true);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    // Fetch paper list on mount
    useEffect(() => {
        (async () => {
            try {
                const res = await listPapers();
                setPapers(res.data);
            } catch (err) {
                setError('Failed to load papers.');
            } finally {
                setLoadingPapers(false);
            }
        })();
    }, []);

    // Auto-scroll to latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleAsk = async (e) => {
        e.preventDefault();
        if (!selectedPaperId || !question.trim()) return;

        const q = question.trim();
        setQuestion('');
        setMessages((prev) => [...prev, { role: 'user', content: q }]);
        setLoading(true);
        setError(null);

        try {
            const res = await askQuestion(Number(selectedPaperId), q);
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: res.data.answer },
            ]);
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to get an answer.';
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: `⚠️ Error: ${msg}` },
            ]);
        } finally {
            setLoading(false);
        }
    };

    /** Clear conversation when paper changes. */
    const handlePaperChange = (e) => {
        setSelectedPaperId(e.target.value);
        setMessages([]);
        setError(null);
    };

    return (
        <div className="qa-container">
            <div className="page-header">
                <h2>💬 Paper Q&A</h2>
                <p>Ask questions about a specific paper using AI-powered analysis.</p>
            </div>

            {/* Paper selector */}
            <div className="qa-select">
                <div className="input-group" style={{ flex: 1 }}>
                    <label htmlFor="paper-select">Select a Paper</label>
                    {loadingPapers ? (
                        <div className="status-message loading" style={{ padding: '8px 12px' }}>
                            <div className="spinner"></div> Loading papers...
                        </div>
                    ) : (
                        <select
                            id="paper-select"
                            value={selectedPaperId}
                            onChange={handlePaperChange}
                            disabled={papers.length === 0}
                        >
                            <option value="">
                                {papers.length === 0
                                    ? '— No papers available. Upload one first. —'
                                    : '— Choose a paper —'}
                            </option>
                            {papers.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.title}
                                </option>
                            ))}
                        </select>
                    )}
                </div>
            </div>

            {/* Chat messages */}
            {messages.length > 0 && (
                <div className="qa-messages">
                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            className={`qa-message ${msg.role}`}
                            id={`qa-msg-${i}`}
                        >
                            {msg.content}
                        </div>
                    ))}
                    {loading && (
                        <div className="qa-message assistant" style={{ opacity: 0.7 }}>
                            <div className="spinner" style={{ display: 'inline-block', marginRight: 8 }}></div>
                            Thinking...
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            )}

            {/* Empty state */}
            {messages.length === 0 && selectedPaperId && (
                <div className="empty-state">
                    <div className="empty-icon">💡</div>
                    <h3>Ask a question</h3>
                    <p>Type a question below to get AI-powered answers from this paper.</p>
                </div>
            )}

            {/* Question input */}
            <form className="qa-input-bar" onSubmit={handleAsk}>
                <input
                    className="input"
                    type="text"
                    placeholder={
                        selectedPaperId
                            ? 'Ask a question about this paper...'
                            : 'Select a paper first'
                    }
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={!selectedPaperId || loading}
                    id="qa-input"
                />
                <button
                    className="btn btn-primary"
                    type="submit"
                    disabled={!selectedPaperId || !question.trim() || loading}
                    id="qa-send-button"
                >
                    {loading ? (
                        <><div className="spinner"></div> Asking...</>
                    ) : (
                        '📨 Ask'
                    )}
                </button>
            </form>

            {error && (
                <div className="status-message error" style={{ marginTop: 12 }}>
                    ❌ {error}
                </div>
            )}
        </div>
    );
}
