/**
 * ResearchHub AI – Literature Review Component
 * Generates structured literature reviews using the agentic pipeline.
 * Renders Markdown output with react-markdown.
 */

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { generateReview } from '../api';

export default function LiteratureReview() {
    const [topic, setTopic] = useState('');
    const [numPapers, setNumPapers] = useState(5);
    const [review, setReview] = useState(null); // { review, papers_used }
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState(null);

    const handleGenerate = async (e) => {
        e.preventDefault();
        if (!topic.trim()) return;

        setGenerating(true);
        setError(null);
        setReview(null);

        try {
            const res = await generateReview(topic.trim(), numPapers);
            setReview(res.data);
        } catch (err) {
            setError(
                err.response?.data?.detail || 'Failed to generate review. Please try again.'
            );
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2>📝 Literature Review</h2>
                <p>Generate an AI-powered literature review from your uploaded papers.</p>
            </div>

            {/* Input form */}
            <form className="review-form" onSubmit={handleGenerate}>
                <div className="input-group">
                    <label htmlFor="review-topic">Research Topic</label>
                    <input
                        className="input"
                        type="text"
                        placeholder="e.g. Deep learning for medical image analysis"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        disabled={generating}
                        id="review-topic"
                    />
                </div>
                <div className="input-group" style={{ maxWidth: 140 }}>
                    <label htmlFor="review-num-papers">Papers</label>
                    <input
                        className="input"
                        type="number"
                        min={2}
                        max={10}
                        value={numPapers}
                        onChange={(e) => setNumPapers(Number(e.target.value))}
                        disabled={generating}
                        id="review-num-papers"
                    />
                </div>
                <button
                    className="btn btn-primary"
                    type="submit"
                    disabled={generating || !topic.trim()}
                    id="generate-review-button"
                    style={{ alignSelf: 'flex-end' }}
                >
                    {generating ? (
                        <><div className="spinner"></div> Generating...</>
                    ) : (
                        '🚀 Generate'
                    )}
                </button>
            </form>

            {/* Loading state */}
            {generating && (
                <div className="status-message loading" style={{ marginBottom: 16 }}>
                    <div className="spinner"></div>
                    Generating literature review... This may take a minute as the AI analyzes multiple papers.
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="status-message error" style={{ marginBottom: 16 }}>
                    ❌ {error}
                </div>
            )}

            {/* Review output */}
            {review && (
                <div>
                    <div className="review-output" id="review-output">
                        <ReactMarkdown>{review.review}</ReactMarkdown>
                    </div>

                    {/* Papers used */}
                    {review.papers_used && review.papers_used.length > 0 && (
                        <div className="papers-used">
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: 8 }}>
                                Papers cited:
                            </span>
                            {review.papers_used.map((title, i) => (
                                <span className="meta-tag" key={i}>📄 {title}</span>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Empty state */}
            {!review && !generating && !error && (
                <div className="empty-state">
                    <div className="empty-icon">🤖</div>
                    <h3>Ready to generate</h3>
                    <p>Enter a research topic above to create a structured literature review from your papers.</p>
                </div>
            )}
        </div>
    );
}
