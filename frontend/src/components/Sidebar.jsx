/**
 * ResearchHub AI – Sidebar Navigation
 */

import React from 'react';

const navItems = [
    { id: 'upload', icon: '📄', label: 'Upload Paper' },
    { id: 'papers', icon: '📚', label: 'My Papers' },
    { id: 'search', icon: '🔍', label: 'Semantic Search' },
    { id: 'qa', icon: '💬', label: 'Paper Q&A' },
    { id: 'review', icon: '📝', label: 'Literature Review' },
];

export default function Sidebar({ activeView, onNavigate }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <h1>ResearchHub AI</h1>
                <p className="tagline">Intelligent Paper Analysis</p>
            </div>
            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <div
                        key={item.id}
                        className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                        onClick={() => onNavigate(item.id)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === 'Enter' && onNavigate(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </div>
                ))}
            </nav>
        </aside>
    );
}
