
import React from 'react';
import { AnalysisResult } from '../../shared/api-client';
import { AlertTriangle, CheckCircle, HelpCircle, Activity, Cpu } from 'lucide-react';

interface ResultsPanelProps {
    result: AnalysisResult;
    onReset: () => void;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ result, onReset }) => {
    const isReal = result.verdict === 'LIKELY_REAL';
    const isFake = result.verdict === 'LIKELY_FAKE';

    const colorClass = isReal
        ? 'text-success border-success/30 bg-success/10'
        : (isFake ? 'text-danger border-danger/30 bg-danger/10' : 'text-warning border-warning/30 bg-warning/10');

    const Icon = isReal ? CheckCircle : (isFake ? AlertTriangle : HelpCircle);

    return (
        <div className="flex flex-col h-full animate-in">
            {/* Header / Verdict */}
            <div className={`p-6 rounded-2xl border ${colorClass} mb-4 text-center relative overflow-hidden backdrop-blur-sm`}>
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

                <Icon className="w-12 h-12 mx-auto mb-2 opacity-90" />
                <h2 className="text-2xl font-bold tracking-tight">{result.verdict?.replace('_', ' ') || 'UNCERTAIN'}</h2>
                <div className="text-sm opacity-80 mt-1 font-mono">
                    CONFIDENCE: {Math.round((result.confidence || 0) * 100)}%
                </div>
            </div>

            {/* Analysis Breakdown */}
            <div className="flex-1 space-y-3 overflow-y-auto pr-1">

                {/* Bio-Guard Card */}
                <div className="glass-card p-4">
                    <div className="flex items-center gap-2 mb-2 text-primary">
                        <Activity className="w-4 h-4" />
                        <h3 className="font-semibold text-sm tracking-wider">BIO-GUARD</h3>
                    </div>

                    <div className="space-y-2 text-sm text-gray-300">
                        <div className="flex justify-between">
                            <span>Pulse Signal</span>
                            <span className={result.bio_guard?.pulse_detected ? "text-success" : "text-gray-500"}>
                                {result.bio_guard?.pulse_detected ? "DETECTED" : "NOT FOUND"}
                            </span>
                        </div>
                        {result.bio_guard?.pulse_detected && (
                            <div className="flex justify-between">
                                <span>Heart Rate</span>
                                <span className="font-mono">{Math.round(result.bio_guard?.bpm || 0)} BPM</span>
                            </div>
                        )}
                        <div className="w-full bg-white/10 h-1.5 rounded-full mt-2 overflow-hidden">
                            <div
                                className="bg-primary h-full rounded-full transition-all duration-1000"
                                style={{ width: `${(result.bio_guard?.confidence || 0) * 100}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Physics-Guard Card */}
                <div className="glass-card p-4">
                    <div className="flex items-center gap-2 mb-2 text-accent">
                        <Cpu className="w-4 h-4" />
                        <h3 className="font-semibold text-sm tracking-wider">PHYSICS-GUARD</h3>
                    </div>

                    <div className="text-sm text-gray-300">
                        {result.physics_guard?.available ? (
                            <>
                                <p className="mb-2 italic opacity-80">"{result.physics_guard?.assessment || "Analysis complete"}"</p>
                                {result.physics_guard?.findings && result.physics_guard.findings.length > 0 && (
                                    <ul className="list-disc list-inside space-y-1 text-xs opacity-75">
                                        {result.physics_guard.findings.slice(0, 2).map((f: string, i: number) => (
                                            <li key={i}>{f}</li>
                                        ))}
                                    </ul>
                                )}
                            </>
                        ) : (
                            <div className="flex items-center gap-2 text-gray-500">
                                <AlertTriangle className="w-3 h-3" />
                                <span>AI Analysis Unavailable</span>
                            </div>
                        )}
                    </div>
                </div>

            </div>

            <button
                onClick={onReset}
                className="mt-4 w-full py-3 rounded-xl border border-white/10 hover:bg-white/5 transition-colors text-sm font-medium text-gray-400"
            >
                Analyze Another Video
            </button>
        </div>
    );
};
