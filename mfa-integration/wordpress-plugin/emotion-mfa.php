<?php
/**
 * Plugin Name: Emotion-Aware MFA
 * Plugin URI: https://emotion-auth.com
 * Description: Add emotion-aware multi-factor authentication to WordPress login
 * Version: 1.0.0
 * Author: Emotion Auth Team
 * Author URI: https://emotion-auth.com
 * License: MIT
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class EmotionMFA_Plugin {
    
    private $api_url;
    private $api_key;
    
    public function __construct() {
        // Get settings
        $this->api_url = get_option('emotion_mfa_api_url', 'http://localhost:8000');
        $this->api_key = get_option('emotion_mfa_api_key', '');
        
        // Hooks
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('login_enqueue_scripts', array($this, 'enqueue_login_scripts'));
        add_action('wp_ajax_nopriv_emotion_mfa_verify', array($this, 'ajax_verify_mfa'));
        add_action('wp_ajax_emotion_mfa_verify', array($this, 'ajax_verify_mfa'));
        add_filter('authenticate', array($this, 'mfa_authenticate'), 30, 3);
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_options_page(
            'Emotion MFA Settings',
            'Emotion MFA',
            'manage_options',
            'emotion-mfa',
            array($this, 'settings_page')
        );
    }
    
    /**
     * Register settings
     */
    public function register_settings() {
        register_setting('emotion_mfa_settings', 'emotion_mfa_api_url');
        register_setting('emotion_mfa_settings', 'emotion_mfa_api_key');
        register_setting('emotion_mfa_settings', 'emotion_mfa_enabled');
        register_setting('emotion_mfa_settings', 'emotion_mfa_require_face');
        register_setting('emotion_mfa_settings', 'emotion_mfa_require_voice');
        register_setting('emotion_mfa_settings', 'emotion_mfa_require_keystroke');
    }
    
    /**
     * Settings page
     */
    public function settings_page() {
        ?>
        <div class="wrap">
            <h1>🔐 Emotion-Aware MFA Settings</h1>
            <form method="post" action="options.php">
                <?php settings_fields('emotion_mfa_settings'); ?>
                <?php do_settings_sections('emotion_mfa_settings'); ?>
                
                <table class="form-table">
                    <tr>
                        <th scope="row">Enable MFA</th>
                        <td>
                            <input type="checkbox" name="emotion_mfa_enabled" value="1" 
                                <?php checked(get_option('emotion_mfa_enabled'), 1); ?>>
                            <p class="description">Enable emotion-aware MFA for login</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">API URL</th>
                        <td>
                            <input type="text" name="emotion_mfa_api_url" 
                                value="<?php echo esc_attr(get_option('emotion_mfa_api_url', 'http://localhost:8000')); ?>" 
                                class="regular-text">
                            <p class="description">URL of your emotion auth API server</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">API Key</th>
                        <td>
                            <input type="text" name="emotion_mfa_api_key" 
                                value="<?php echo esc_attr(get_option('emotion_mfa_api_key', '')); ?>" 
                                class="regular-text">
                            <p class="description">API authentication key</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">Biometric Factors</th>
                        <td>
                            <label>
                                <input type="checkbox" name="emotion_mfa_require_face" value="1" 
                                    <?php checked(get_option('emotion_mfa_require_face', 1), 1); ?>>
                                Facial Recognition
                            </label><br>
                            
                            <label>
                                <input type="checkbox" name="emotion_mfa_require_voice" value="1" 
                                    <?php checked(get_option('emotion_mfa_require_voice', 1), 1); ?>>
                                Voice Analysis
                            </label><br>
                            
                            <label>
                                <input type="checkbox" name="emotion_mfa_require_keystroke" value="1" 
                                    <?php checked(get_option('emotion_mfa_require_keystroke', 1), 1); ?>>
                                Keystroke Dynamics
                            </label>
                        </td>
                    </tr>
                </table>
                
                <?php submit_button(); ?>
            </form>
            
            <hr>
            
            <h2>📊 Test Connection</h2>
            <button type="button" class="button" onclick="testConnection()">Test API Connection</button>
            <div id="test-result" style="margin-top: 10px;"></div>
            
            <script>
            function testConnection() {
                const apiUrl = document.querySelector('input[name="emotion_mfa_api_url"]').value;
                const resultDiv = document.getElementById('test-result');
                
                resultDiv.innerHTML = 'Testing connection...';
                
                fetch(apiUrl + '/docs')
                    .then(response => {
                        if (response.ok) {
                            resultDiv.innerHTML = '<span style="color: green;">✅ Connection successful!</span>';
                        } else {
                            resultDiv.innerHTML = '<span style="color: red;">❌ Connection failed</span>';
                        }
                    })
                    .catch(error => {
                        resultDiv.innerHTML = '<span style="color: red;">❌ Error: ' + error.message + '</span>';
                    });
            }
            </script>
        </div>
        <?php
    }
    
    /**
     * Enqueue scripts on login page
     */
    public function enqueue_login_scripts() {
        if (!get_option('emotion_mfa_enabled')) {
            return;
        }
        
        wp_enqueue_script(
            'emotion-mfa-plugin',
            plugins_url('emotion-mfa-plugin.js', __FILE__),
            array(),
            '1.0.0',
            true
        );
        
        wp_localize_script('emotion-mfa-plugin', 'emotionMFAConfig', array(
            'apiUrl' => $this->api_url,
            'apiKey' => $this->api_key,
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'requireFace' => get_option('emotion_mfa_require_face', 1),
            'requireVoice' => get_option('emotion_mfa_require_voice', 1),
            'requireKeystroke' => get_option('emotion_mfa_require_keystroke', 1)
        ));
        
        // Add custom login script
        wp_add_inline_script('emotion-mfa-plugin', $this->get_login_script());
    }
    
    /**
     * Get login script
     */
    private function get_login_script() {
        return "
        jQuery(document).ready(function($) {
            const mfa = new EmotionMFA({
                apiUrl: emotionMFAConfig.apiUrl,
                apiKey: emotionMFAConfig.apiKey
            });
            
            const originalForm = $('#loginform');
            let mfaPending = false;
            
            originalForm.on('submit', function(e) {
                if (mfaPending) {
                    return true;
                }
                
                e.preventDefault();
                
                const username = $('#user_login').val();
                const password = $('#user_pass').val();
                
                // Show loading
                $('#wp-submit').val('Verifying MFA...');
                $('#wp-submit').prop('disabled', true);
                
                // Perform MFA
                mfa.verify(username, {
                    requireFace: emotionMFAConfig.requireFace == 1,
                    requireVoice: emotionMFAConfig.requireVoice == 1,
                    requireKeystroke: emotionMFAConfig.requireKeystroke == 1
                }).then(function(result) {
                    if (result.success) {
                        // Store MFA result and submit form
                        $('<input>').attr({
                            type: 'hidden',
                            name: 'emotion_mfa_verified',
                            value: '1'
                        }).appendTo(originalForm);
                        
                        $('<input>').attr({
                            type: 'hidden',
                            name: 'emotion_mfa_data',
                            value: JSON.stringify(result)
                        }).appendTo(originalForm);
                        
                        mfaPending = true;
                        originalForm.submit();
                    } else {
                        alert('MFA verification failed: ' + result.message);
                        $('#wp-submit').val('Log In');
                        $('#wp-submit').prop('disabled', false);
                    }
                }).catch(function(error) {
                    alert('MFA error: ' + error.message);
                    $('#wp-submit').val('Log In');
                    $('#wp-submit').prop('disabled', false);
                });
            });
        });
        ";
    }
    
    /**
     * MFA authentication filter
     */
    public function mfa_authenticate($user, $username, $password) {
        if (!get_option('emotion_mfa_enabled')) {
            return $user;
        }
        
        // Skip if already error
        if (is_wp_error($user)) {
            return $user;
        }
        
        // Check if MFA was verified
        if (!isset($_POST['emotion_mfa_verified']) || $_POST['emotion_mfa_verified'] != '1') {
            return new WP_Error('mfa_required', 'MFA verification required');
        }
        
        // Verify MFA data
        if (!isset($_POST['emotion_mfa_data'])) {
            return new WP_Error('mfa_invalid', 'Invalid MFA data');
        }
        
        $mfa_data = json_decode(stripslashes($_POST['emotion_mfa_data']), true);
        
        if (!$mfa_data || !$mfa_data['success']) {
            return new WP_Error('mfa_failed', 'MFA verification failed');
        }
        
        // Log successful MFA
        $this->log_mfa_attempt($username, true, $mfa_data);
        
        return $user;
    }
    
    /**
     * AJAX verify MFA
     */
    public function ajax_verify_mfa() {
        $user_id = sanitize_text_field($_POST['user_id']);
        $frame_data = sanitize_text_field($_POST['frame_data']);
        $voice_features = json_decode(stripslashes($_POST['voice_features']), true);
        $keystroke_events = json_decode(stripslashes($_POST['keystroke_events']), true);
        
        $result = $this->verify_mfa_api($user_id, $frame_data, $voice_features, $keystroke_events);
        
        wp_send_json($result);
    }
    
    /**
     * Call MFA API
     */
    private function verify_mfa_api($user_id, $frame_data, $voice_features, $keystroke_events) {
        $response = wp_remote_post($this->api_url . '/api/auth/attempt', array(
            'headers' => array(
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . $this->api_key
            ),
            'body' => json_encode(array(
                'user_id' => $user_id,
                'frame_data_url' => $frame_data,
                'voice_features' => $voice_features,
                'keystroke_events' => $keystroke_events
            )),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            return array(
                'success' => false,
                'message' => 'API error: ' . $response->get_error_message()
            );
        }
        
        $body = json_decode(wp_remote_retrieve_body($response), true);
        
        if (!$body || !$body['ok']) {
            return array(
                'success' => false,
                'message' => 'Verification failed'
            );
        }
        
        return array(
            'success' => $body['fusion']['decision'] === 'permit',
            'decision' => $body['fusion']['decision'],
            'confidence' => $body['fusion']['confidence'],
            'message' => $body['fusion']['guidance']
        );
    }
    
    /**
     * Log MFA attempt
     */
    private function log_mfa_attempt($username, $success, $data) {
        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'username' => $username,
            'success' => $success,
            'decision' => $data['decision'] ?? 'unknown',
            'confidence' => $data['confidence'] ?? 0,
            'ip_address' => $_SERVER['REMOTE_ADDR']
        );
        
        // Store in WordPress option or custom table
        $logs = get_option('emotion_mfa_logs', array());
        array_unshift($logs, $log_entry);
        $logs = array_slice($logs, 0, 100); // Keep last 100 entries
        update_option('emotion_mfa_logs', $logs);
    }
}

// Initialize plugin
new EmotionMFA_Plugin();
