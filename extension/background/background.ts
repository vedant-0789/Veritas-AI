
// Background script
// Handles any cross-origin requests or state management if needed in future
// Currently, content script handles direct API calls to localhost

import { apiClient } from '../shared/api-client';

chrome.runtime.onInstalled.addListener(() => {
    console.log('Veritas-AI Extension installed');
});

const addToHistory = (result: any) => {
    chrome.storage.local.get(['veritas_history'], (data) => {
        const history = data.veritas_history || [];
        const newItem = {
            id: result.task_id || Date.now().toString(),
            date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            verdict: result.verdict || 'UNKNOWN',
            confidence: result.confidence || 0
        };
        const updated = [newItem, ...history].slice(0, 10);
        chrome.storage.local.set({ veritas_history: updated });
    });
};

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'PING') {
        sendResponse({ status: 'pong' });
        return false;
    }

    if (request.type === 'ANALYZE_REQUEST') {
        console.log("Background: Received analysis request", request.data.frames.length, "frames");

        // Return true to indicate async response
        (async () => {
            try {
                console.log("Background: Submitting analysis to backend...");
                const initialResult = await apiClient.analyzeVideo(request.data);
                console.log("Background: Task submitted successfully. TaskID:", initialResult.task_id);

                console.log("Background: Waiting for analysis completion (polling)...");
                const finalResult = await apiClient.waitForAnalysis(initialResult.task_id);
                console.log("Background: Analysis completed successfully!");

                addToHistory(finalResult);
                sendResponse({ success: true, result: finalResult });

            } catch (error: any) {
                console.error("Background: Analysis process failed:", error);
                const errorMsg = error?.message || "Unknown background error";
                sendResponse({ success: false, error: errorMsg });
            }
        })();

        return true; // Keep message channel open for async response
    }
    // ...
    // Helper to save history (Moved to top)


    if (request.type === 'HEALTH_CHECK') {
        apiClient.healthCheck()
            .then(isHealthy => {
                sendResponse({ healthy: isHealthy });
            })
            .catch(() => {
                sendResponse({ healthy: false });
            });
        return true;
    }

    if (request.type === 'CAPTURE_TAB') {
        const windowId = sender.tab?.windowId;
        if (!windowId) {
            sendResponse({ success: false, error: "No window ID" });
            return true;
        }
        chrome.tabs.captureVisibleTab(windowId, { format: 'jpeg', quality: 80 }, (dataUrl) => {
            if (chrome.runtime.lastError) {
                sendResponse({ success: false, error: chrome.runtime.lastError.message });
            } else {
                sendResponse({ success: true, dataUrl });
            }
        });
        return true;
    }
});
