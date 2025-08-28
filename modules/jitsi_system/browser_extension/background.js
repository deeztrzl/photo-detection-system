// Background script untuk browser extension
// Handle extension lifecycle dan communication

chrome.runtime.onInstalled.addListener((details) => {
    console.log('🎥 Jitsi KTP Capture Extension installed');
    
    if (details.reason === 'install') {
        // Set default settings
        chrome.storage.sync.set({
            'ktp-capture-enabled': true,
            'auto-capture-mode': false,
            'detection-confidence': 0.5,
            'bridge-url': 'http://localhost:5001'
        });
        
        // Open welcome page
        chrome.tabs.create({
            url: chrome.runtime.getURL('welcome.html')
        });
    }
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // Check if current tab is Jitsi Meet
    if (isJitsiMeetTab(tab.url)) {
        // Toggle capture panel
        chrome.tabs.sendMessage(tab.id, {
            action: 'toggle-capture-panel'
        });
    } else {
        // Show info notification
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: 'KTP Capture',
            message: 'Please navigate to a Jitsi Meet room to use this extension.'
        });
    }
});

// Handle messages dari content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    switch (request.action) {
        case 'get-settings':
            getSettings().then(sendResponse);
            return true; // Keep message channel open
            
        case 'save-settings':
            saveSettings(request.settings).then(() => {
                sendResponse({ success: true });
            });
            return true;
            
        case 'capture-completed':
            handleCaptureCompleted(request.data);
            sendResponse({ success: true });
            break;
            
        case 'show-notification':
            showNotification(request.title, request.message, request.type);
            sendResponse({ success: true });
            break;
            
        default:
            sendResponse({ error: 'Unknown action' });
    }
});

// Handle tab updates untuk detect Jitsi Meet
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && isJitsiMeetTab(tab.url)) {
        // Inject content script jika belum ada
        chrome.tabs.sendMessage(tabId, { action: 'ping' })
            .catch(() => {
                // Content script not loaded, inject it
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['capture-engine.js', 'jitsi-injector.js']
                });
            });
    }
});

// Utility functions
function isJitsiMeetTab(url) {
    if (!url) return false;
    
    const jitsiDomains = [
        'meet.jit.si',
        '.jitsi.net',
        '8x8.vc',
        'jitsi.org'
    ];
    
    return jitsiDomains.some(domain => url.includes(domain));
}

async function getSettings() {
    return new Promise((resolve) => {
        chrome.storage.sync.get([
            'ktp-capture-enabled',
            'auto-capture-mode', 
            'detection-confidence',
            'bridge-url',
            'cs-mode'
        ], (result) => {
            resolve({
                enabled: result['ktp-capture-enabled'] ?? true,
                autoCapture: result['auto-capture-mode'] ?? false,
                confidence: result['detection-confidence'] ?? 0.5,
                bridgeUrl: result['bridge-url'] ?? 'http://localhost:5001',
                csMode: result['cs-mode'] ?? false
            });
        });
    });
}

async function saveSettings(settings) {
    return new Promise((resolve) => {
        const settingsToSave = {
            'ktp-capture-enabled': settings.enabled,
            'auto-capture-mode': settings.autoCapture,
            'detection-confidence': settings.confidence,
            'bridge-url': settings.bridgeUrl,
            'cs-mode': settings.csMode
        };
        
        chrome.storage.sync.set(settingsToSave, resolve);
    });
}

function handleCaptureCompleted(data) {
    // Show success notification
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'KTP Capture Completed',
        message: `Capture completed for ${data.participantName || 'participant'}`
    });
    
    // Log untuk analytics (jika dibutuhkan)
    console.log('Capture completed:', data);
}

function showNotification(title, message, type = 'basic') {
    const iconUrl = type === 'error' ? 'icons/error.png' : 'icons/icon48.png';
    
    chrome.notifications.create({
        type: 'basic',
        iconUrl: iconUrl,
        title: title,
        message: message
    });
}

// Handle notification clicks
chrome.notifications.onClicked.addListener((notificationId) => {
    // Clear notification
    chrome.notifications.clear(notificationId);
    
    // Focus on Jitsi tab jika ada
    chrome.tabs.query({ url: '*://meet.jit.si/*' }, (tabs) => {
        if (tabs.length > 0) {
            chrome.tabs.update(tabs[0].id, { active: true });
            chrome.windows.update(tabs[0].windowId, { focused: true });
        }
    });
});

// Cleanup on extension disable/uninstall
chrome.runtime.onSuspend.addListener(() => {
    console.log('🎥 KTP Capture Extension suspended');
});

// Handle storage changes untuk sync settings across tabs
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'sync') {
        // Broadcast settings update ke active tabs
        chrome.tabs.query({ url: '*://meet.jit.si/*' }, (tabs) => {
            tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'settings-updated',
                    changes: changes
                }).catch(() => {
                    // Tab might not have content script loaded
                });
            });
        });
    }
});

// Periodic health check untuk bridge connection
setInterval(async () => {
    const settings = await getSettings();
    
    if (settings.enabled) {
        try {
            const response = await fetch(`${settings.bridgeUrl}/api/health`);
            const health = await response.json();
            
            // Store health status
            chrome.storage.local.set({
                'bridge-health': health,
                'bridge-last-check': Date.now()
            });
            
        } catch (error) {
            chrome.storage.local.set({
                'bridge-health': { status: 'error', error: error.message },
                'bridge-last-check': Date.now()
            });
        }
    }
}, 30000); // Check every 30 seconds
