/**
 * ResearchHub AI – Paper List Component
 * Displays all uploaded papers with metadata in a styled grid.
 */

import React, { useState, useEffect } from 'react';
import { listPapers } from '../api';

export default function PaperList() {
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchPapers();
    }, []);

    const fetchPapers = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await listPapers();
            setPapers(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load papers.');
        } finally {
            setLoading(false);
        }
    };

    /** Format ISO date string to readable format. */
    const formatDate = (iso) => {
        return new Date(iso).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <div>
            <div className="page-header">
                <h2>📚 My Papers</h2>
                <p>Browse all uploaded and indexed research papers.</p>
            </div>

            {loading && (
                <div className="status-message loading">
                    <div className="spinner"></div>
                    Loading papers...
                </div>
            )}

            {error && (
                <div className="status-message error">❌ {error}</div>
            )}

            {!loading && !error && papers.length === 0 && (
                <div className="empty-state">
                    <div className="empty-icon">📭</div>
                    <h3>No papers yet</h3>
                    <p>Upload your first PDF to get started.</p>
                </div>
            )}

            {!loading && papers.length > 0 && (
                <div className="paper-grid">
                    {papers.map((paper) => (
                        <div className="paper-item" key={paper.id} id={`paper-${paper.id}`}>
                            <div className="paper-title">{paper.title}</div>
                            <div className="paper-meta">
                                {paper.authors && (
                                    <span className="meta-tag">👤 {paper.authors}</span>
                                )}
                                {paper.page_count && (
                                    <span className="meta-tag">📄 {paper.page_count} pages</span>
                                )}
                                <span className="meta-tag">🕐 {formatDate(paper.uploaded_at)}</span>
                            </div>
                            {paper.abstract && (
                                <div className="paper-abstract">{paper.abstract}</div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
