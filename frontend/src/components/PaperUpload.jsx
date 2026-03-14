/**
 * ResearchHub AI – Paper Upload Component
 * Drag-and-drop PDF upload with progress feedback.
 */

import React, { useState, useRef } from 'react';
import { uploadPaper } from '../api';

export default function PaperUpload({ onUploadSuccess }) {
    const [dragOver, setDragOver] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState(null); // { type, message }
    const fileRef = useRef(null);

    const handleFile = async (file) => {
        if (!file) return;
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            setStatus({ type: 'error', message: 'Only PDF files are accepted.' });
            return;
        }

        setUploading(true);
        setStatus({ type: 'loading', message: `Uploading "${file.name}"... This may take a moment.` });

        try {
            const res = await uploadPaper(file);
            setStatus({ type: 'success', message: res.data.message });
            if (onUploadSuccess) onUploadSuccess(res.data.paper);
        } catch (err) {
            const msg = err.response?.data?.detail || 'Upload failed. Please try again.';
            setStatus({ type: 'error', message: msg });
        } finally {
            setUploading(false);
        }
    };

    const onDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        handleFile(file);
    };

    const onDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const onDragLeave = () => setDragOver(false);

    const onClick = () => {
        if (!uploading) fileRef.current?.click();
    };

    const onFileChange = (e) => {
        handleFile(e.target.files[0]);
        e.target.value = '';
    };

    return (
        <div>
            <div className="page-header">
                <h2>📄 Upload Paper</h2>
                <p>Upload a PDF research paper to extract, embed, and index it.</p>
            </div>

            <div
                className={`upload-zone ${dragOver ? 'dragover' : ''}`}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onClick={onClick}
                role="button"
                tabIndex={0}
                id="upload-zone"
            >
                <div className="upload-icon">📤</div>
                <h3>{uploading ? 'Processing...' : 'Drop your PDF here'}</h3>
                <p>{uploading ? 'Parsing, embedding, and indexing your paper' : 'or click to browse files'}</p>
                {uploading && <div className="spinner" style={{ margin: '16px auto 0' }}></div>}
            </div>

            <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                onChange={onFileChange}
                style={{ display: 'none' }}
                id="file-input"
            />

            {status && (
                <div className={`status-message ${status.type}`} style={{ marginTop: 16 }}>
                    {status.type === 'loading' && <div className="spinner"></div>}
                    {status.type === 'success' && '✅'}
                    {status.type === 'error' && '❌'}
                    {status.message}
                </div>
            )}
        </div>
    );
}
