/**
 * Emotion-Aware MFA Plugin
 * 
 * Easy integration for any website to add emotion-based multi-factor authentication.
 * 
 * Usage:
 *   <script src="emotion-mfa-plugin.js"></script>
 *   <script>
 *     const mfa = new EmotionMFA({
 *       apiUrl: 'https://your-emotion-auth-server.com',
 *       apiKey: 'your-api-key'
 *     });
 *     
 *     // After primary authentication (username/password)
 *     mfa.verify(userId).then(result => {
 *       if (result.success) {
 *         // Grant access
 *       }
 *     });
 *   </script>
 */

class EmotionMFA {
    constructor(config = {}) {
        this.apiUrl = config.apiUrl || 'http://localhost:8000';
        this.apiKey = config.apiKey || '';
        this.timeout = config.timeout || 30000;
        this.theme = config.theme || 'light';
        this.language = config.language || 'en';
        this.onProgress = config.onProgress || null;
        
        // UI elements
        this.modal = null;
        this.videoElement = null;
        this.stream = null;
        
        // Data collection
        this.frameData = null;
        this.voiceFeatures = null;
        this.keystrokeEvents = [];
        
        this.init();
    }
    
    init() {
        // Inject CSS
        this.injectStyles();
    }
    
    /**
     * Main verification method - call this after primary authentication
     */
    async verify(userId, options = {}) {
        return new Promise((resolve, reject) => {
            this.userId = userId;
            this.options = {
                requireFace: options.requireFace !== false,
                requireVoice: options.requireVoice !== false,
                requireKeystroke: options.requireKeystroke !== false,
                passphrase: options.passphrase || 'Please say: I am logging in securely',
                ...options
            };
            
            this.showModal();
            this.startVerification()
                .then(result => {
                    this.hideModal();
                    resolve(result);
                })
                .catch(error => {
                    this.hideModal();
                    reject(error);
                });
        });
    }
    
    /**
     * Quick verify - minimal UI, automatic capture
     */
    async quickVerify(userId) {
        try {
            // Capture data silently
            await this.captureFrame();
            await this.captureVoice(2000); // 2 second voice sample
            
            // Send to API
            const result = await this.sendVerification();
            return result;
        } catch (error) {
            throw new Error(`Quick verification failed: ${error.message}`);
        }
    }
    
    /**
     * Start the verification process
     */
    async startVerification() {
        try {
            this.updateProgress('Initializing...', 10);
            
            // Step 1: Capture facial data
            if (this.options.requireFace) {
                this.updateProgress('Capturing facial data...', 30);
                await this.captureFrame();
            }
            
            // Step 2: Capture voice data
            if (this.options.requireVoice) {
                this.updateProgress('Recording voice sample...', 50);
                await this.captureVoice();
            }
            
            // Step 3: Capture keystroke data
            if (this.options.requireKeystroke) {
                this.updateProgress('Analyzing typing pattern...', 70);
                await this.captureKeystroke();
            }
            
            // Step 4: Send to API
            this.updateProgress('Verifying...', 90);
            const result = await this.sendVerification();
            
            this.updateProgress('Complete!', 100);
            
            return {
                success: result.decision === 'permit',
                decision: result.decision,
                confidence: result.confidence,
                message: result.guidance,
                details: result
            };
            
        } catch (error) {
            throw new Error(`Verification failed: ${error.message}`);
        }
    }
    
    /**
     * Capture facial frame
     */
    async captureFrame() {
        return new Promise(async (resolve, reject) => {
            try {
                // Request camera access
                this.stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                
                // Create video element
                const video = document.createElement('video');
                video.srcObject = this.stream;
                video.autoplay = true;
                
                // Wait for video to be ready
                video.onloadedmetadata = () => {
                    setTimeout(() => {
                        // Capture frame
                        const canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0);
                        
                        this.frameData = canvas.toDataURL('image/jpeg', 0.8);
                        
                        // Stop camera
                        this.stream.getTracks().forEach(track => track.stop());
                        
                        resolve();
                    }, 1000); // Wait 1 second for camera to adjust
                };
                
            } catch (error) {
                reject(new Error(`Camera access denied: ${error.message}`));
            }
        });
    }
    
    /**
     * Capture voice sample
     */
    async captureVoice(duration = 3000) {
        return new Promise(async (resolve, reject) => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();
                source.connect(analyser);
                
                analyser.fftSize = 2048;
                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);
                
                // Collect audio features
                const features = { rms: [], zcr: [], pitch: [] };
                const startTime = Date.now();
                
                const collectFeatures = () => {
                    if (Date.now() - startTime < duration) {
                        analyser.getByteTimeDomainData(dataArray);
                        
                        // Calculate RMS
                        let sum = 0;
                        for (let i = 0; i < bufferLength; i++) {
                            const normalized = (dataArray[i] - 128) / 128;
                            sum += normalized * normalized;
                        }
                        features.rms.push(Math.sqrt(sum / bufferLength));
                        
                        // Calculate ZCR
                        let zcr = 0;
                        for (let i = 1; i < bufferLength; i++) {
                            if ((dataArray[i] >= 128 && dataArray[i-1] < 128) ||
                                (dataArray[i] < 128 && dataArray[i-1] >= 128)) {
                                zcr++;
                            }
                        }
                        features.zcr.push(zcr / bufferLength);
                        
                        requestAnimationFrame(collectFeatures);
                    } else {
                        // Stop recording
                        stream.getTracks().forEach(track => track.stop());
                        
                        // Calculate averages
                        this.voiceFeatures = {
                            rms: features.rms.reduce((a, b) => a + b, 0) / features.rms.length,
                            zcr: features.zcr.reduce((a, b) => a + b, 0) / features.zcr.length,
                            pitch_hz: 150 + Math.random() * 100 // Simplified
                        };
                        
                        resolve();
                    }
                };
                
                collectFeatures();
                
            } catch (error) {
                reject(new Error(`Microphone access denied: ${error.message}`));
            }
        });
    }
    
    /**
     * Capture keystroke pattern
     */
    async captureKeystroke() {
        return new Promise((resolve) => {
            this.keystrokeEvents = [];
            
            // Show input field
            const input = document.createElement('input');
            input.type = 'text';
            input.placeholder = this.options.passphrase || 'Type your passphrase';
            input.className = 'emotion-mfa-input';
            
            const container = this.modal.querySelector('.emotion-mfa-content');
            container.appendChild(input);
            
            input.focus();
            
            // Track keystrokes
            input.addEventListener('keydown', (e) => {
                this.keystrokeEvents.push({
                    key: e.key,
                    t_down: Date.now(),
                    t_up: null
                });
            });
            
            input.addEventListener('keyup', (e) => {
                const lastEvent = this.keystrokeEvents[this.keystrokeEvents.length - 1];
                if (lastEvent && lastEvent.key === e.key) {
                    lastEvent.t_up = Date.now();
                }
            });
            
            // Wait for Enter key or timeout
            const timeout = setTimeout(() => {
                container.removeChild(input);
                resolve();
            }, 10000);
            
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    clearTimeout(timeout);
                    container.removeChild(input);
                    resolve();
                }
            });
        });
    }
    
    /**
     * Send verification data to API
     */
    async sendVerification() {
        const payload = {
            user_id: this.userId,
            frame_data_url: this.frameData || '',
            voice_features: this.voiceFeatures || { rms: 0.3, zcr: 0.2, pitch_hz: 180 },
            keystroke_events: this.keystrokeEvents.length > 0 ? this.keystrokeEvents : [
                { key: 'a', t_down: 100, t_up: 150 }
            ]
        };
        
        const response = await fetch(`${this.apiUrl}/api/auth/attempt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.ok) {
            throw new Error(data.detail || 'Verification failed');
        }
        
        return {
            decision: data.fusion.decision,
            confidence: data.fusion.confidence,
            guidance: data.fusion.guidance,
            emotional_state: data.fusion.emotional_state,
            stress_level: data.fusion.stress,
            raw: data
        };
    }
    
    /**
     * Show modal UI
     */
    showModal() {
        this.modal = document.createElement('div');
        this.modal.className = `emotion-mfa-modal emotion-mfa-${this.theme}`;
        this.modal.innerHTML = `
            <div class="emotion-mfa-overlay"></div>
            <div class="emotion-mfa-container">
                <div class="emotion-mfa-header">
                    <h2>🔐 Multi-Factor Authentication</h2>
                    <button class="emotion-mfa-close">&times;</button>
                </div>
                <div class="emotion-mfa-content">
                    <div class="emotion-mfa-progress">
                        <div class="emotion-mfa-progress-bar" style="width: 0%"></div>
                    </div>
                    <p class="emotion-mfa-message">Initializing verification...</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
        
        // Close button
        this.modal.querySelector('.emotion-mfa-close').addEventListener('click', () => {
            this.hideModal();
        });
    }
    
    /**
     * Hide modal UI
     */
    hideModal() {
        if (this.modal) {
            document.body.removeChild(this.modal);
            this.modal = null;
        }
        
        // Clean up streams
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
    
    /**
     * Update progress
     */
    updateProgress(message, percent) {
        if (this.modal) {
            const progressBar = this.modal.querySelector('.emotion-mfa-progress-bar');
            const messageEl = this.modal.querySelector('.emotion-mfa-message');
            
            if (progressBar) progressBar.style.width = `${percent}%`;
            if (messageEl) messageEl.textContent = message;
        }
        
        if (this.onProgress) {
            this.onProgress(message, percent);
        }
    }
    
    /**
     * Inject CSS styles
     */
    injectStyles() {
        if (document.getElementById('emotion-mfa-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'emotion-mfa-styles';
        style.textContent = `
            .emotion-mfa-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .emotion-mfa-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(5px);
            }
            
            .emotion-mfa-container {
                position: relative;
                max-width: 500px;
                margin: 100px auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                overflow: hidden;
            }
            
            .emotion-mfa-light .emotion-mfa-container {
                background: white;
                color: #333;
            }
            
            .emotion-mfa-dark .emotion-mfa-container {
                background: #1e1e1e;
                color: #fff;
            }
            
            .emotion-mfa-header {
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .emotion-mfa-header h2 {
                margin: 0;
                font-size: 20px;
                font-weight: 600;
            }
            
            .emotion-mfa-close {
                background: none;
                border: none;
                color: white;
                font-size: 28px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                line-height: 1;
            }
            
            .emotion-mfa-content {
                padding: 30px;
            }
            
            .emotion-mfa-progress {
                width: 100%;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 20px;
            }
            
            .emotion-mfa-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                transition: width 0.3s ease;
            }
            
            .emotion-mfa-message {
                text-align: center;
                font-size: 16px;
                margin: 20px 0;
            }
            
            .emotion-mfa-input {
                width: 100%;
                padding: 12px;
                border: 2px solid #667eea;
                border-radius: 6px;
                font-size: 16px;
                margin-top: 10px;
                box-sizing: border-box;
            }
            
            .emotion-mfa-input:focus {
                outline: none;
                border-color: #764ba2;
            }
        `;
        
        document.head.appendChild(style);
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmotionMFA;
}
if (typeof define === 'function' && define.amd) {
    define([], function() { return EmotionMFA; });
}
if (typeof window !== 'undefined') {
    window.EmotionMFA = EmotionMFA;
}
