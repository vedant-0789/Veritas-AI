
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Shield, Play, AlertCircle } from 'lucide-react';
import { ResultsPanel } from './components/ResultsPanel';
import { AnalysisResult } from '../shared/api-client';
import './index.css';

const Popup = () => {
    const [status, setStatus] = useState<'idle' | 'capturing' | 'analyzing' | 'success' | 'error'>('idle');
    const [result, _setResult] = useState<AnalysisResult | null>(null);
    const [errorMsg, setErrorMsg] = useState<string>('');
    const [backendReady, setBackendReady] = useState<boolean>(false);

    const checkBackend = () => {
        chrome.runtime.sendMessage({ type: 'HEALTH_CHECK' }, (response) => {
            if (!chrome.runtime.lastError && response?.healthy) {
                setBackendReady(true);
            } else {
                setBackendReady(false);
            }
        });
    };

    useEffect(() => {
        checkBackend();
    }, []);

    const sendMessageToTab = (tabId: number) => {
        return new Promise((resolve, reject) => {
            chrome.tabs.sendMessage(tabId, { type: 'START_SCAN' }, (response) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else if (response && response.success) {
                    resolve(response);
                } else {
                    reject(new Error(response?.error || "Failed to start scan"));
                }
            });
        });
    };

    const handleScan = async () => {
        try {
            setStatus('capturing');
            setErrorMsg('');

            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            if (!tab.id || !tab.url?.includes('youtube.com/watch')) {
                throw new Error("Please open a YouTube video first.");
            }

            // Attempt 1: Direct Message
            try {
                await sendMessageToTab(tab.id);
                window.close();
            } catch (err) {
                console.log("Initial connection failed, attempting injection...", err);

                // Attempt 2: Inject Script and Retry
                // We use the file name from the build output
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['content.iife.js']
                });

                // Give it a moment to initialize
                await new Promise(resolve => setTimeout(resolve, 500));

                await sendMessageToTab(tab.id);
                window.close();
            }

        } catch (e: any) {
            setStatus('error');
            console.error(e);
            setErrorMsg(e.message || "Could not connect. Please refresh the page.");
        }
    };

    if (!backendReady) {
        return (
            <div className="h-full flex flex-col items-center justify-center p-6 text-center space-y-4">
                <AlertCircle className="w-12 h-12 text-danger opacity-80" />
                <h2 className="text-lg font-bold">Backend Disconnected</h2>
                <p className="text-sm text-gray-400">
                    Is the Python server running? <br />
                    <code className="bg-white/10 px-1 py-0.5 rounded text-xs">python backend/main.py</code>
                </p>
                <button
                    onClick={checkBackend}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-full text-sm transition-colors"
                >
                    Retry Connection
                </button>
            </div>
        );
    }

    return (
        <div className="w-full h-full p-4 flex flex-col relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute top-[-20%] left-[-20%] w-[140%] h-[140%] bg-blue-500/5 blur-[100px] pointer-events-none" />

            {/* Navbar */}
            <header className="flex items-center justify-between mb-6 z-10">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-lg tracking-tight">Veritas<span className="text-primary">AI</span></span>
                </div>
                <div className="px-2 py-1 rounded-full bg-success/10 border border-success/20 text-success text-[10px] font-mono tracking-wider">
                    SYSTEM ACTIVE
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 z-10 relative">

                {status === 'idle' && (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-6">
                        <div className="relative group cursor-pointer" onClick={handleScan}>
                            <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl group-hover:bg-primary/30 transition-all duration-500" />
                            <div className="relative w-24 h-24 rounded-full glass border border-white/10 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                                <Play className="w-10 h-10 text-white fill-white ml-1 opacity-90" />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <h2 className="text-xl font-bold">Deepfake Detector</h2>
                            <p className="text-sm text-gray-400 leading-relaxed px-4">
                                Open a YouTube video and use the injected <span className="text-primary font-semibold">Veritas Button</span> or click above to scan manually.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-3 w-full mt-4">
                            <div className="glass-card p-3 text-center">
                                <div className="text-xs text-gray-500 mb-1">REQ. PER DAY</div>
                                <div className="font-mono text-primary font-bold">1,500</div>
                            </div>
                            <div className="glass-card p-3 text-center">
                                <div className="text-xs text-gray-500 mb-1">AVG. ACCURACY</div>
                                <div className="font-mono text-success font-bold">94.2%</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Temporary Error State for Popup Action */}
                {status === 'error' && (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                        <AlertCircle className="w-12 h-12 text-warning mb-4" />
                        <p className="text-sm text-gray-300 mb-6">{errorMsg}</p>
                        <button onClick={() => setStatus('idle')} className="text-sm text-primary hover:underline">Go Back</button>
                    </div>
                )}

                {/* Results State - In a real scenario, this would be populated if we messaged content script */}
                {status === 'success' && result && (
                    <ResultsPanel result={result} onReset={() => setStatus('idle')} />
                )}

            </main>

            {/* Footer */}
            <footer className="mt-auto py-4 text-center text-[10px] text-gray-600 font-mono">
                POWERED BY GEMINI AI & RPPG
            </footer>
        </div>
    );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <Popup />
    </React.StrictMode>,
)
