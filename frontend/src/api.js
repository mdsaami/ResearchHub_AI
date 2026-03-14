/**
 * ResearchHub AI – API Client
 * Centralized Axios instance for all backend communication.
 */

import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    timeout: 120000, // 2 min timeout for AI operations
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Upload a PDF paper.
 * @param {File} file - The PDF file to upload.
 * @returns {Promise} Response with paper metadata.
 */
export const uploadPaper = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/papers/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

/** List all uploaded papers. */
export const listPapers = async () => api.get('/papers/');

/** Get a single paper by ID. */
export const getPaper = async (id) => api.get(`/papers/${id}`);

/**
 * Semantic search for papers.
 * @param {string} query - Natural language search query.
 * @param {number} topK - Number of results.
 */
export const searchPapers = async (query, topK = 5) =>
    api.post('/search/', { query, top_k: topK });

/**
 * Ask a question about a specific paper.
 * @param {number} paperId - ID of the paper.
 * @param {string} question - The question to ask.
 */
export const askQuestion = async (paperId, question) =>
    api.post('/qa/', { paper_id: paperId, question });

/**
 * Generate a literature review on a topic.
 * @param {string} topic - Research topic.
 * @param {number} numPapers - Number of papers to include.
 */
export const generateReview = async (topic, numPapers = 5) =>
    api.post('/review/', { topic, num_papers: numPapers });

export default api;
