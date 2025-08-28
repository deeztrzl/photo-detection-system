/**
 * Jitsi Meet KTP Capture Injector
 * Main content script untuk inject capture functionality ke Jitsi Meet
 */

class JitsiCaptureInjector {
    constructor() {
        this.isInitialized = false;
        this.captureEngine = null;
        this.socket = null;
        this.sessionId = null;
        this.participantId = null;
        this.isCSMode = false;
        this.participants = new Map();
        this.overlayActive = false;
        
        // Configuration
        this.config = {
            bridgeUrl: 'http://localhost:5001',
            captureInterval: 100, // ms
            maxRetries: 3,
            debug: true
        };
        
        this.init();
    }
    
    async init() {
        try {
            this.log('🎥 Initializing Jitsi KTP Capture...');
            
            // Wait for Jitsi to fully load
            await this.waitForJitsiLoad();
            
            // Extract session info dari URL
            this.extractSessionInfo();
            
            // Initialize capture engine
            this.captureEngine = new CaptureEngine(this.config);
            await this.captureEngine.init();
            
            // Setup WebSocket connection
            await this.setupWebSocket();
            
            // Inject UI components
            this.injectCaptureUI();
            
            // Setup video monitoring
            this.setupVideoMonitoring();
            
            // Join session
            this.joinCaptureSession();
            
            this.isInitialized = true;
            this.log('✅ Jitsi KTP Capture initialized successfully');
            
        } catch (error) {
            this.log('❌ Initialization failed:', error);
        }
    }
    
    waitForJitsiLoad() {
        return new Promise((resolve) => {
            const maxWait = 30000; // 30 seconds
            const startTime = Date.now();
            
            const checkJitsi = () => {
                // Check untuk berbagai indikator bahwa Jitsi sudah load
                const jitsiLoaded = (
                    window.APP && 
                    window.APP.conference &&
                    document.querySelector('#new-toolbox') &&
                    document.querySelector('.participants-pane')
                );
                
                if (jitsiLoaded) {
                    this.log('✅ Jitsi Meet loaded');
                    resolve();
                } else if (Date.now() - startTime > maxWait) {
                    this.log('⚠️ Jitsi load timeout, proceeding anyway...');
                    resolve();
                } else {
                    setTimeout(checkJitsi, 500);
                }
            };
            
            checkJitsi();
        });
    }
    
    extractSessionInfo() {
        // Extract room name dari URL
        const urlPath = window.location.pathname;
        this.sessionId = urlPath.substring(1) || 'default-room';
        
        // Generate participant ID
        this.participantId = 'user_' + Math.random().toString(36).substr(2, 9);
        
        // Detect CS mode (bisa dari URL parameter atau local storage)
        const urlParams = new URLSearchParams(window.location.search);
        this.isCSMode = urlParams.get('role') === 'cs' || 
                       localStorage.getItem('jitsi-ktp-role') === 'cs';
        
        this.log(`📍 Session: ${this.sessionId}, Participant: ${this.participantId}, CS Mode: ${this.isCSMode}`);
    }
    
    async setupWebSocket() {
        try {
            // Load Socket.IO dari CDN jika belum tersedia
            if (typeof io === 'undefined') {
                await this.loadScript('https://cdn.socket.io/4.7.2/socket.io.min.js');
            }
            
            this.socket = io(this.config.bridgeUrl, {
                transports: ['websocket', 'polling'],
                timeout: 5000
            });
            
            this.socket.on('connect', () => {
                this.log('🔗 Connected to bridge server');
            });
            
            this.socket.on('disconnect', () => {
                this.log('❌ Disconnected from bridge server');
            });
            
            this.socket.on('capture_requested', (data) => {
                this.handleCaptureRequest(data);
            });
            
            this.socket.on('capture_completed', (data) => {
                this.handleCaptureCompleted(data);
            });
            
            this.socket.on('overlay_sync', (data) => {
                this.handleOverlaySync(data);
            });
            
            this.socket.on('session_joined', (data) => {
                this.updateParticipantsList(data);
            });
            
        } catch (error) {
            this.log('❌ WebSocket setup failed:', error);
        }
    }
    
    injectCaptureUI() {
        // Inject capture button ke Jitsi toolbar
        this.injectToolbarButton();
        
        // Inject control panel (untuk CS)
        if (this.isCSMode) {
            this.injectControlPanel();
        }
        
        // Inject overlay system
        this.injectOverlaySystem();
    }
    
    injectToolbarButton() {
        const toolbar = document.querySelector('#new-toolbox');
        if (!toolbar) {
            this.log('⚠️ Toolbar not found, trying alternative selectors...');
            return;
        }
        
        // Create capture button
        const captureButton = document.createElement('div');
        captureButton.className = 'toolbox-button';
        captureButton.id = 'ktp-capture-button';
        captureButton.innerHTML = `
            <div class="toolbox-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9,2V7.38L10.5,8.88L15.12,4.26L19.74,8.88L12,16.62L4.26,8.88L8.88,4.26L9,4.17V2H9M12,14.2L17.8,8.4L16.4,7L12,11.4L7.6,7L6.2,8.4L12,14.2Z"/>
                </svg>
            </div>
            <span class="toolbox-label">KTP Capture</span>
        `;
        
        captureButton.addEventListener('click', () => {
            this.toggleCapturePanel();
        });
        
        // Insert before last child (usually overflow menu)
        const lastButton = toolbar.lastElementChild;
        toolbar.insertBefore(captureButton, lastButton);
        
        this.log('✅ Capture button injected');
    }
    
    injectControlPanel() {
        const panel = document.createElement('div');
        panel.id = 'ktp-capture-panel';
        panel.className = 'ktp-capture-panel hidden';
        panel.innerHTML = `
            <div class="panel-header">
                <h3>🎯 KTP Capture Control</h3>
                <button class="close-btn" onclick="this.parentElement.parentElement.classList.add('hidden')">&times;</button>
            </div>
            <div class="panel-content">
                <div class="session-info">
                    <p><strong>Session:</strong> <span id="session-display">${this.sessionId}</span></p>
                    <p><strong>Mode:</strong> <span class="cs-badge">CS Mode</span></p>
                </div>
                
                <div class="participants-section">
                    <h4>👥 Participants</h4>
                    <div id="participants-list" class="participants-list">
                        <div class="loading">Loading participants...</div>
                    </div>
                </div>
                
                <div class="capture-controls">
                    <button id="auto-capture-btn" class="btn btn-primary">
                        🤖 Auto Capture
                    </button>
                    <button id="manual-capture-btn" class="btn btn-secondary">
                        📸 Manual Capture
                    </button>
                    <button id="toggle-overlay-btn" class="btn btn-accent">
                        👁️ Toggle Overlay
                    </button>
                </div>
                
                <div class="status-section">
                    <div class="status-indicator">
                        <span class="status-dot"></span>
                        <span id="status-text">Ready</span>
                    </div>
                    <div id="detection-info" class="detection-info"></div>
                </div>
                
                <div class="recent-captures">
                    <h4>📁 Recent Captures</h4>
                    <div id="captures-list" class="captures-list">
                        <div class="empty-state">No captures yet</div>
                    </div>
                </div>
            </div>
        `;
        
        // Event listeners
        panel.querySelector('#auto-capture-btn').addEventListener('click', () => {
            this.startAutoCapture();
        });
        
        panel.querySelector('#manual-capture-btn').addEventListener('click', () => {
            this.triggerManualCapture();
        });
        
        panel.querySelector('#toggle-overlay-btn').addEventListener('click', () => {
            this.toggleOverlay();
        });
        
        document.body.appendChild(panel);
        this.log('✅ Control panel injected');
    }
    
    injectOverlaySystem() {
        const overlay = document.createElement('div');
        overlay.id = 'ktp-overlay-system';
        overlay.className = 'ktp-overlay-system hidden';
        overlay.innerHTML = `
            <div class="overlay-guides">
                <div class="face-guide">
                    <div class="guide-label">👤 Face Area</div>
                </div>
                <div class="ktp-guide">
                    <div class="guide-label">🆔 KTP Area</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        this.log('✅ Overlay system injected');
    }
    
    setupVideoMonitoring() {
        // Monitor video elements untuk capture
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.tagName === 'VIDEO') {
                        this.handleNewVideo(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Process existing videos
        document.querySelectorAll('video').forEach(video => {
            this.handleNewVideo(video);
        });
        
        this.log('✅ Video monitoring setup complete');
    }
    
    handleNewVideo(videoElement) {
        if (videoElement.dataset.ktpMonitored) return;
        
        videoElement.dataset.ktpMonitored = 'true';
        
        // Extract participant info dari video element
        const participantInfo = this.extractParticipantInfo(videoElement);
        
        if (participantInfo) {
            this.participants.set(participantInfo.id, {
                ...participantInfo,
                videoElement: videoElement,
                lastCapture: null
            });
            
            this.updateParticipantsUI();
            this.log(`👤 New participant detected: ${participantInfo.name}`);
        }
    }
    
    extractParticipantInfo(videoElement) {
        // Try to extract participant info dari Jitsi DOM structure
        let participantContainer = videoElement.closest('[data-participantid]');
        
        if (!participantContainer) {
            // Alternative method
            participantContainer = videoElement.closest('.participant');
        }
        
        if (participantContainer) {
            const participantId = participantContainer.dataset.participantid || 
                                videoElement.id || 
                                'participant_' + Math.random().toString(36).substr(2, 6);
            
            // Try to get participant name
            const nameElement = participantContainer.querySelector('.displayname') ||
                               participantContainer.querySelector('.participant-name') ||
                               participantContainer.querySelector('[data-testid="participant-name"]');
            
            const participantName = nameElement ? 
                                  nameElement.textContent.trim() : 
                                  `Participant ${participantId.substr(-4)}`;
            
            return {
                id: participantId,
                name: participantName,
                isLocal: participantContainer.classList.contains('local') || 
                        videoElement.muted,
                element: participantContainer
            };
        }
        
        return null;
    }
    
    updateParticipantsUI() {
        const participantsList = document.getElementById('participants-list');
        if (!participantsList) return;
        
        if (this.participants.size === 0) {
            participantsList.innerHTML = '<div class="empty-state">No participants detected</div>';
            return;
        }
        
        participantsList.innerHTML = '';
        
        this.participants.forEach((participant, id) => {
            const participantItem = document.createElement('div');
            participantItem.className = 'participant-item';
            participantItem.innerHTML = `
                <div class="participant-info">
                    <span class="participant-name">${participant.name}</span>
                    <span class="participant-status ${participant.isLocal ? 'local' : 'remote'}">
                        ${participant.isLocal ? '👤 You' : '👥 Remote'}
                    </span>
                </div>
                <div class="participant-actions">
                    <button class="btn-small capture-btn" data-participant="${id}">
                        📸 Capture
                    </button>
                </div>
            `;
            
            // Add event listener
            participantItem.querySelector('.capture-btn').addEventListener('click', () => {
                this.captureParticipant(id);
            });
            
            participantsList.appendChild(participantItem);
        });
    }
    
    joinCaptureSession() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('join_session', {
                session_id: this.sessionId,
                user_type: this.isCSMode ? 'cs' : 'participant',
                user_id: this.participantId
            });
            
            this.log(`🚪 Joined session: ${this.sessionId}`);
        }
    }
    
    toggleCapturePanel() {
        const panel = document.getElementById('ktp-capture-panel');
        if (panel) {
            panel.classList.toggle('hidden');
        }
    }
    
    toggleOverlay() {
        this.overlayActive = !this.overlayActive;
        const overlay = document.getElementById('ktp-overlay-system');
        
        if (overlay) {
            overlay.classList.toggle('hidden', !this.overlayActive);
        }
        
        // Broadcast overlay state
        if (this.socket) {
            this.socket.emit('overlay_update', {
                session_id: this.sessionId,
                overlay_data: {
                    active: this.overlayActive,
                    timestamp: Date.now()
                }
            });
        }
        
        this.updateStatus(this.overlayActive ? 'Overlay Active' : 'Overlay Hidden');
    }
    
    async captureParticipant(participantId) {
        const participant = this.participants.get(participantId);
        if (!participant) {
            this.showNotification('Participant not found', 'error');
            return;
        }
        
        try {
            this.updateStatus(`Capturing ${participant.name}...`);
            
            // Capture video frame
            const imageData = await this.captureVideoFrame(participant.videoElement);
            
            if (!imageData) {
                throw new Error('Failed to capture video frame');
            }
            
            // Send ke bridge untuk processing
            const response = await fetch(`${this.config.bridgeUrl}/api/process_capture`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    participant_id: participantId,
                    image_data: imageData,
                    capture_mode: 'manual',
                    timestamp: new Date().toISOString()
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.handleCaptureSuccess(result);
            } else {
                throw new Error(result.message || 'Capture failed');
            }
            
        } catch (error) {
            this.log('❌ Capture error:', error);
            this.showNotification(`Capture failed: ${error.message}`, 'error');
            this.updateStatus('Ready');
        }
    }
    
    async captureVideoFrame(videoElement) {
        if (!videoElement || videoElement.videoWidth === 0) {
            return null;
        }
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        ctx.drawImage(videoElement, 0, 0);
        
        // Convert ke base64
        return canvas.toDataURL('image/jpeg', 0.8);
    }
    
    handleCaptureSuccess(result) {
        this.updateStatus('Capture successful!');
        
        // Auto-download files
        if (result.zip_file) {
            this.downloadFile(result.zip_file, result.zip_filename);
        }
        
        // Update UI
        this.addCaptureToHistory(result);
        this.showNotification('Capture completed successfully! Files downloading...', 'success');
        
        // Update participant last capture
        const participant = this.participants.get(result.participant_id);
        if (participant) {
            participant.lastCapture = Date.now();
        }
    }
    
    downloadFile(base64Data, filename) {
        const link = document.createElement('a');
        link.href = 'data:application/octet-stream;base64,' + base64Data;
        link.download = filename;
        link.click();
        
        this.log(`📥 Downloaded: ${filename}`);
    }
    
    addCaptureToHistory(captureResult) {
        const capturesList = document.getElementById('captures-list');
        if (!capturesList) return;
        
        // Remove empty state
        const emptyState = capturesList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        const captureItem = document.createElement('div');
        captureItem.className = 'capture-item';
        captureItem.innerHTML = `
            <div class="capture-info">
                <strong>${this.participants.get(captureResult.participant_id)?.name || 'Unknown'}</strong>
                <span class="timestamp">${new Date(captureResult.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="capture-results">
                ${captureResult.face_detected ? '✅ Face' : '❌ Face'}
                ${captureResult.ktp_detected ? '✅ KTP' : '❌ KTP'}
            </div>
        `;
        
        capturesList.insertBefore(captureItem, capturesList.firstChild);
        
        // Keep only last 5 captures
        while (capturesList.children.length > 5) {
            capturesList.removeChild(capturesList.lastChild);
        }
    }
    
    handleCaptureRequest(data) {
        if (data.participant_id === this.participantId) {
            this.log('📸 Capture requested for this participant');
            // Auto-trigger capture jika ini participant yang diminta
            this.captureParticipant(this.participantId);
        }
    }
    
    handleCaptureCompleted(data) {
        this.log('✅ Capture completed notification:', data);
        this.showNotification(`Capture completed for ${data.participant_id}`, 'success');
    }
    
    handleOverlaySync(data) {
        // Sync overlay state dengan CS
        if (data.overlay_data) {
            this.overlayActive = data.overlay_data.active;
            const overlay = document.getElementById('ktp-overlay-system');
            if (overlay) {
                overlay.classList.toggle('hidden', !this.overlayActive);
            }
        }
    }
    
    updateStatus(message, type = 'info') {
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (statusText) {
            statusText.textContent = message;
        }
        
        if (statusDot) {
            statusDot.className = `status-dot ${type}`;
        }
        
        this.log(`📊 Status: ${message}`);
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `ktp-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">
                    ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
                </span>
                <span class="notification-message">${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    async loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    log(...args) {
        if (this.config.debug) {
            console.log('[KTP Capture]', ...args);
        }
    }
}

// Initialize saat DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => new JitsiCaptureInjector(), 1000);
    });
} else {
    setTimeout(() => new JitsiCaptureInjector(), 1000);
}
