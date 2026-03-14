/**
 * ResearchHub AI – Main Application Layout
 * Renders sidebar navigation and switches between views.
 */

import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import PaperUpload from './components/PaperUpload';
import PaperList from './components/PaperList';
import SemanticSearch from './components/SemanticSearch';
import PaperQA from './components/PaperQA';
import LiteratureReview from './components/LiteratureReview';

export default function App() {
    const [activeView, setActiveView] = useState('upload');

    /** Called after a successful upload to auto-switch to the papers list. */
    const handleUploadSuccess = () => {
        // Small delay so the success message is visible before switching
        setTimeout(() => setActiveView('papers'), 1200);
    };

    const renderView = () => {
        switch (activeView) {
            case 'upload':
                return <PaperUpload onUploadSuccess={handleUploadSuccess} />;
            case 'papers':
                return <PaperList />;
            case 'search':
                return <SemanticSearch />;
            case 'qa':
                return <PaperQA />;
            case 'review':
                return <LiteratureReview />;
            default:
                return <PaperUpload onUploadSuccess={handleUploadSuccess} />;
        }
    };

    return (
        <div className="app-layout">
            <Sidebar activeView={activeView} onNavigate={setActiveView} />
            <main className="main-content">
                {renderView()}
            </main>
        </div>
    );
}
