/**
 * ResearchHub AI – Semantic Search Component
 * Natural language search over uploaded papers with relevance scores.
 */

import React, { useState } from 'react';
import { searchPapers } from '../api';

export default function SemanticSearch() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [searching, setSearching] = useState(false);
    const [searched, setSearched] = useState(false);
    const [error, setError] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setSearching(true);
        setError(null);
        setResults([]);

        try {
            const res = await searchPapers(query.trim());
            setResults(res.data.results);
            setSearched(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Search failed. Please try again.');
        } finally {
            setSearching(false);
        }
    };

    /** Convert score (0-1) to a percentage string. */
    const scorePercent = (score) => `${(score * 100).toFixed(1)}%`;

    return (
        <div>
            <div className="page-header">
                <h2>🔍 Semantic Search</h2>
                <p>Search your paper collection using natural language queries.</p>
            </div>

            {/* Search bar */}
            <form className="search-bar" onSubmit={handleSearch}>
                <input
                    className="input"
                    type="text"
                    placeholder="e.g. What papers discuss transformer architectures for NLP?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={searching}
                    id="search-input"
                />
                <button
                    className="btn btn-primary"
                    type="submit"
                    disabled={searching || !query.trim()}
                    id="search-button"
                >
                    {searching ? (
                        <><div className="spinner"></div> Searching...</>
                    ) : (
                        '🔎 Search'
                    )}
                </button>
            </form>

            {/* Error */}
            {error && (
                <div className="status-message error">❌ {error}</div>
            )}

            {/* Results */}
            {results.length > 0 && (
                <div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: 16, fontSize: '0.85rem' }}>
                        Found {results.length} relevant paper{results.length !== 1 ? 's' : ''}
                    </p>
                    {results.map((r, i) => (
                        <div className="search-result" key={`${r.paper_id}-${i}`} id={`result-${r.paper_id}`}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                                <div className="paper-title" style={{ fontWeight: 600, fontSize: '1rem' }}>
                                    {r.title}
                                </div>
                                <span className="score-badge">
                                    ✨ {scorePercent(r.score)}
                                </span>
                            </div>
                            {r.authors && (
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                                    👤 {r.authors}
                                </div>
                            )}
                            {r.abstract && (
                                <div className="paper-abstract">{r.abstract}</div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* No results */}
            {searched && !searching && results.length === 0 && !error && (
                <div className="empty-state">
                    <div className="empty-icon">🔎</div>
                    <h3>No results found</h3>
                    <p>Try a different query or upload more papers.</p>
                </div>
            )}
        </div>
    );
}
