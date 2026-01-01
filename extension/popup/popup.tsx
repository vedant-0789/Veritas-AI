import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Shield, Play, AlertCircle, History, Clock, Trash2, Cpu } from 'lucide-react';
import './index.css';

interface HistoryItem {
    id: string;
    date: string;
    verdict: string;
    confidence: number;
    thumbnail?: string; // Potential future feature
}

const Popup = () => {
    const [status, setStatus] = useState<'idle' | 'capturing' | 'analyzing' | 'success' | 'error'>('idle');
    const [errorMsg, setErrorMsg] = useState<string>('');
    const [backendReady, setBackendReady] = useState<boolean>(false);

    // New Features State
    const [useGemini, setUseGemini] = useState<boolean>(true);
    const [showHistory, setShowHistory] = useState<boolean>(false);
    const [scanHistory, setScanHistory] = useState<HistoryItem[]>([]);

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
        // Load history from chrome.storage
        chrome.storage.local.get(['veritas_history'], (data) => {
            if (data.veritas_history) {
                setScanHistory(data.veritas_history);
            }
        });
    }, []);

    const clearHistory = () => {
        setScanHistory([]);
        chrome.storage.local.remove('veritas_history');
    };

    const sendMessageToTab = (tabId: number) => {
        return new Promise((resolve, reject) => {
            chrome.tabs.sendMessage(tabId, {
                type: 'START_SCAN',
                options: { enable_gemini: useGemini }
            }, (response) => {
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
                window.close(); // Close popup as the injected UI takes over
            } catch (err) {
                console.log("Initial connection failed, attempting injection...", err);

                // Attempt 2: Inject Script and Retry
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

    // History View
    if (showHistory) {
        return (
            <div className="w-full h-full p-4 flex flex-col relative overflow-hidden bg-background">
                <div className="flex items-center justify-between mb-4">
                    <button onClick={() => setShowHistory(false)} className="text-sm text-gray-400 hover:text-white flex items-center gap-1">
                        ← Back
                    </button>
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-gray-500">HISTORY</span>
                        <button onClick={clearHistory} className="p-1 hover:bg-white/10 rounded-full text-gray-500 hover:text-danger transition-colors">
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                    {scanHistory.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 text-sm opacity-60">
                            <History className="w-8 h-8 mb-2" />
                            No recent scans
                        </div>
                    ) : (
                        scanHistory.map((item) => (
                            <div key={item.id} className="glass-card p-3 flex items-center justify-between hover:bg-white/5 transition-colors">
                                <div>
                                    <div className={`font-bold text-sm ${item.verdict.includes('REAL') ? 'text-success' : (item.verdict.includes('FAKE') ? 'text-danger' : 'text-warning')}`}>
                                        {item.verdict.replace('LIKELY_', '')}
                                    </div>
                                    <div className="text-[10px] text-gray-400 flex items-center gap-1">
                                        <Clock className="w-3 h-3" /> {item.date}
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs font-mono font-bold text-white/50">{Math.round(item.confidence * 100)}%</div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
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

                <button
                    onClick={() => setShowHistory(true)}
                    className="p-2 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-primary"
                    title="View History"
                >
                    <History className="w-5 h-5" />
                </button>
            </header>

            {/* Main Content */}
            <main className="flex-1 z-10 relative flex flex-col">

                {status === 'idle' && (
                    <div className="h-full flex flex-col">

                        {/* Settings Card */}
                        <div className="glass-card p-4 mb-6">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
                                    <Cpu className="w-4 h-4 text-accent" />
                                    AI Physics Guard
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={useGemini}
                                        onChange={() => setUseGemini(!useGemini)}
                                    />
                                    <div className="w-9 h-5 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                                </label>
                            </div>
                            <p className="text-[10px] text-gray-500 leading-tight">
                                Uses Gemini AI to detect physics anomalies. Disable to use only Bio-Guard (rPPG) and save API quota.
                            </p>
                        </div>

                        {/* Scanner Area */}
                        <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
                            <div className="relative group cursor-pointer" onClick={handleScan}>
                                <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl group-hover:bg-primary/30 transition-all duration-500" />
                                <div className="relative w-24 h-24 rounded-full glass border border-white/10 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                                    <Play className="w-10 h-10 text-white fill-white ml-1 opacity-90" />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <h2 className="text-xl font-bold">Deepfake Detector</h2>
                                <p className="text-sm text-gray-400 leading-relaxed px-4">
                                    {useGemini
                                        ? "Full multi-modal analysis enabled."
                                        : "Fast Bio-Guard mode enabled."}
                                    <br />Click to scan current video.
                                </p>
                            </div>
                        </div>

                        {/* Stats Footer */}
                        <div className="grid grid-cols-2 gap-3 w-full mt-auto">
                            <div className="glass-card p-3 text-center">
                                <div className="text-[10px] text-gray-500 mb-1">MODE</div>
                                <div className={`font-mono font-bold text-xs ${useGemini ? 'text-accent' : 'text-primary'}`}>
                                    {useGemini ? 'FULL SUITE' : 'BIO-ONLY'}
                                </div>
                            </div>
                            <div className="glass-card p-3 text-center">
                                <div className="text-[10px] text-gray-500 mb-1">HISTORY</div>
                                <div className="font-mono text-white font-bold text-xs">{scanHistory.length} SCANS</div>
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

                {/* Results State - Not used in popup flow currently as we close window, but kept for future manual mode */}

            </main>

            <footer className="mt-4 pt-4 border-t border-white/5 text-center text-[10px] text-gray-600 font-mono flex items-center justify-center gap-2">
                <span>v1.1.0 (DEV)</span>
                <span>•</span>
                <span>{useGemini ? 'GEMINI ACTIVE' : 'LOCAL ONLY'}</span>
            </footer>
        </div>
    );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <Popup />
    </React.StrictMode>,
)
