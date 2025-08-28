/**
 * Capture Engine for KTP and Face Detection
 * Handles AI processing dan image capture logic
 */

class CaptureEngine {
    constructor(config) {
        this.config = config;
        this.isInitialized = false;
        this.faceDetector = null;
        this.detectionResults = new Map();
        this.processingQueue = [];
        this.isProcessing = false;
        
        // Detection settings
        this.settings = {
            faceMinConfidence: 0.5,
            ktpBlueThreshold: 0.05,
            processingInterval: 100,
            maxQueueSize: 10
        };
    }
    
    async init() {
        try {
            console.log('🔧 Initializing Capture Engine...');
            
            // Initialize MediaPipe Face Detection (via CDN)
            await this.initializeFaceDetection();
            
            // Setup processing worker
            this.startProcessingWorker();
            
            this.isInitialized = true;
            console.log('✅ Capture Engine initialized');
            
        } catch (error) {
            console.error('❌ Capture Engine initialization failed:', error);
            throw error;
        }
    }
    
    async initializeFaceDetection() {
        try {
            // Load MediaPipe dari CDN
            if (!window.FaceDetection) {
                await this.loadMediaPipe();
            }
            
            // Initialize face detector
            this.faceDetector = new window.FaceDetection({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection@0.4/${file}`;
                }
            });
            
            this.faceDetector.setOptions({
                model: 'short',
                minDetectionConfidence: this.settings.faceMinConfidence
            });
            
            this.faceDetector.onResults((results) => {
                this.processFaceResults(results);
            });
            
            console.log('✅ MediaPipe Face Detection loaded');
            
        } catch (error) {
            console.warn('⚠️ MediaPipe unavailable, using fallback detection');
            this.faceDetector = null;
        }
    }
    
    async loadMediaPipe() {
        // Load MediaPipe libraries
        const scripts = [
            'https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3/camera_utils.js',
            'https://cdn.jsdelivr.net/npm/@mediapipe/control_utils@0.6/control_utils.js',
            'https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3/drawing_utils.js',
            'https://cdn.jsdelivr.net/npm/@mediapipe/face_detection@0.4/face_detection.js'
        ];
        
        for (const src of scripts) {
            await this.loadScript(src);
        }
    }
    
    loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve(); // Already loaded
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    startProcessingWorker() {
        // Process queue dengan interval
        setInterval(() => {
            this.processQueue();
        }, this.settings.processingInterval);
    }
    
    async processFrame(videoElement, participantId) {
        if (!this.isInitialized || !videoElement) return null;
        
        try {
            // Add ke queue
            const frameData = {
                participantId,
                timestamp: Date.now(),
                element: videoElement
            };
            
            // Limit queue size
            if (this.processingQueue.length >= this.settings.maxQueueSize) {
                this.processingQueue.shift(); // Remove oldest
            }
            
            this.processingQueue.push(frameData);
            
            return this.detectionResults.get(participantId);
            
        } catch (error) {
            console.error('Frame processing error:', error);
            return null;
        }
    }
    
    async processQueue() {
        if (this.isProcessing || this.processingQueue.length === 0) return;
        
        this.isProcessing = true;
        
        try {
            const frameData = this.processingQueue.shift();
            await this.processFrameData(frameData);
        } catch (error) {
            console.error('Queue processing error:', error);
        } finally {
            this.isProcessing = false;
        }
    }
    
    async processFrameData(frameData) {
        const { participantId, element } = frameData;
        
        try {
            // Capture frame dari video element
            const imageData = await this.captureVideoFrame(element);
            if (!imageData) return;
            
            // Face detection
            const faceResult = await this.detectFace(imageData);
            
            // KTP detection (simplified)
            const ktpResult = this.detectKTP(imageData);
            
            // Store results
            const results = {
                participantId,
                timestamp: Date.now(),
                face: faceResult,
                ktp: ktpResult,
                overall: {
                    detected: faceResult.detected || ktpResult.detected,
                    confidence: Math.max(faceResult.confidence, ktpResult.confidence)
                }
            };
            
            this.detectionResults.set(participantId, results);
            
            // Trigger UI update
            this.updateDetectionUI(participantId, results);
            
        } catch (error) {
            console.error('Frame data processing error:', error);
        }
    }
    
    async captureVideoFrame(videoElement) {
        if (!videoElement || videoElement.videoWidth === 0) return null;
        
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            
            ctx.drawImage(videoElement, 0, 0);
            
            // Get ImageData untuk processing
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            
            return {
                imageData,
                canvas,
                dataUrl: canvas.toDataURL('image/jpeg', 0.8)
            };
            
        } catch (error) {
            console.error('Video frame capture error:', error);
            return null;
        }
    }
    
    async detectFace(frameData) {
        const result = {
            detected: false,
            confidence: 0,
            count: 0,
            faces: []
        };
        
        try {
            if (this.faceDetector && frameData.imageData) {
                // MediaPipe detection
                await this.faceDetector.send({ image: frameData.imageData });
                
                // Results akan diproses di processFaceResults callback
                // Untuk sync purposes, kita gunakan simple detection
                result.detected = this.lastFaceResults && this.lastFaceResults.detections.length > 0;
                result.count = this.lastFaceResults ? this.lastFaceResults.detections.length : 0;
                result.confidence = result.detected ? 0.8 : 0;
                
            } else {
                // Fallback: simple skin tone detection
                const skinDetection = this.detectSkinTone(frameData.imageData);
                result.detected = skinDetection.ratio > 0.15; // 15% skin pixels
                result.confidence = Math.min(skinDetection.ratio * 5, 1);
            }
            
        } catch (error) {
            console.error('Face detection error:', error);
        }
        
        return result;
    }
    
    detectKTP(frameData) {
        const result = {
            detected: false,
            confidence: 0,
            area: 0,
            blueRatio: 0
        };
        
        try {
            if (!frameData.imageData) return result;
            
            const data = frameData.imageData.data;
            const width = frameData.imageData.width;
            const height = frameData.imageData.height;
            const totalPixels = width * height;
            
            let bluePixels = 0;
            
            // Scan untuk blue pixels (KTP Indonesia dominantly blue)
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                
                // Blue detection criteria
                if (this.isBluePixel(r, g, b)) {
                    bluePixels++;
                }
            }
            
            const blueRatio = bluePixels / totalPixels;
            
            result.blueRatio = blueRatio;
            result.area = bluePixels;
            result.detected = blueRatio > this.settings.ktpBlueThreshold;
            result.confidence = Math.min(blueRatio * 20, 1); // Scale confidence
            
        } catch (error) {
            console.error('KTP detection error:', error);
        }
        
        return result;
    }
    
    isBluePixel(r, g, b) {
        // Improved blue detection untuk KTP Indonesia
        return (
            b > r && b > g &&  // Blue is dominant
            b > 80 &&          // Minimum blue intensity
            (b - Math.max(r, g)) > 30 && // Blue significantly higher
            r < 150 && g < 150 // Not too much red/green
        );
    }
    
    detectSkinTone(imageData) {
        const data = imageData.data;
        const totalPixels = imageData.width * imageData.height;
        let skinPixels = 0;
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            if (this.isSkinPixel(r, g, b)) {
                skinPixels++;
            }
        }
        
        return {
            ratio: skinPixels / totalPixels,
            count: skinPixels
        };
    }
    
    isSkinPixel(r, g, b) {
        // Simple skin tone detection
        return (
            r > 95 && g > 40 && b > 20 &&
            Math.max(r, g, b) - Math.min(r, g, b) > 15 &&
            Math.abs(r - g) > 15 && r > g && r > b
        );
    }
    
    processFaceResults(results) {
        this.lastFaceResults = results;
        
        // Update global detection status
        const faceDetected = results.detections && results.detections.length > 0;
        
        // Broadcast detection update
        this.broadcastDetectionUpdate({
            type: 'face',
            detected: faceDetected,
            count: results.detections ? results.detections.length : 0,
            timestamp: Date.now()
        });
    }
    
    updateDetectionUI(participantId, results) {
        // Update detection info di UI
        const detectionInfo = document.getElementById('detection-info');
        if (detectionInfo) {
            detectionInfo.innerHTML = `
                <div class="detection-item">
                    <span class="detection-label">👤 Face:</span>
                    <span class="detection-value ${results.face.detected ? 'detected' : 'not-detected'}">
                        ${results.face.detected ? '✅ Detected' : '❌ Not Found'}
                    </span>
                    <span class="confidence">(${(results.face.confidence * 100).toFixed(0)}%)</span>
                </div>
                <div class="detection-item">
                    <span class="detection-label">🆔 KTP:</span>
                    <span class="detection-value ${results.ktp.detected ? 'detected' : 'not-detected'}">
                        ${results.ktp.detected ? '✅ Detected' : '❌ Not Found'}
                    </span>
                    <span class="confidence">(${(results.ktp.confidence * 100).toFixed(0)}%)</span>
                </div>
            `;
        }
        
        // Update participant item
        const participantBtn = document.querySelector(`[data-participant="${participantId}"]`);
        if (participantBtn) {
            const hasDetection = results.face.detected || results.ktp.detected;
            participantBtn.classList.toggle('has-detection', hasDetection);
            participantBtn.title = `Face: ${results.face.detected ? '✅' : '❌'}, KTP: ${results.ktp.detected ? '✅' : '❌'}`;
        }
    }
    
    broadcastDetectionUpdate(update) {
        // Broadcast ke other components
        window.dispatchEvent(new CustomEvent('ktpDetectionUpdate', {
            detail: update
        }));
    }
    
    getDetectionResults(participantId) {
        return this.detectionResults.get(participantId);
    }
    
    getAllDetectionResults() {
        return Array.from(this.detectionResults.entries()).map(([id, results]) => ({
            participantId: id,
            ...results
        }));
    }
    
    clearDetectionResults(participantId = null) {
        if (participantId) {
            this.detectionResults.delete(participantId);
        } else {
            this.detectionResults.clear();
        }
    }
    
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        
        // Update face detector settings jika available
        if (this.faceDetector) {
            this.faceDetector.setOptions({
                minDetectionConfidence: this.settings.faceMinConfidence
            });
        }
    }
    
    getStats() {
        return {
            initialized: this.isInitialized,
            faceDetectorAvailable: !!this.faceDetector,
            activeParticipants: this.detectionResults.size,
            queueSize: this.processingQueue.length,
            isProcessing: this.isProcessing,
            settings: this.settings
        };
    }
}

// Export untuk use dalam other modules
window.CaptureEngine = CaptureEngine;
