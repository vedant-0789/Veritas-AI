
/**
 * API Client
 * Handles communication with the local Python backend
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface AnalysisRequest {
    frames: Array<{ data: string; timestamp: number }>;
    video_url?: string;
    consent_given: boolean;
}

export interface AnalysisResult {
    task_id: string;
    status: 'processing' | 'completed' | 'error';
    verdict?: 'LIKELY_REAL' | 'LIKELY_FAKE' | 'UNCERTAIN';
    confidence?: number;
    evidence?: string[];
    summary?: string;
    assessment?: string; // Legacy field
    bio_guard?: any;
    physics_guard?: any;
}

export class ApiClient {
    /**
     * Check if backend is available
     */
    async healthCheck(): Promise<boolean> {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return response.ok;
        } catch (e) {
            return false;
        }
    }

    /**
     * Submit video frames for analysis (Sync)
     */
    async analyzeVideoSync(request: AnalysisRequest): Promise<AnalysisResult> {
        try {
            const response = await fetch(`${API_BASE_URL}/analyze-sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (e) {
            console.error("API Error:", e);
            throw e;
        }
    }

    /**
     * Submit video frames for analysis (Async)
     */
    async analyzeVideo(request: AnalysisRequest): Promise<AnalysisResult> {
        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (e) {
            console.error("API Error:", e);
            throw e;
        }
    }

    /**
     * Poll for analysis status
     */
    async getStatus(taskId: string): Promise<AnalysisResult> {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${taskId}`);

            if (!response.ok) {
                throw new Error(`Status check failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (e) {
            console.error("API Error:", e);
            throw e;
        }
    }
}

export const apiClient = new ApiClient();
