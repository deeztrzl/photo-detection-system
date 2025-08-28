"""
KTP Detection Module - Template-Based Detection System dengan Advanced Texture Analysis
Menggunakan enhanced template management untuk adaptive template selection
Features: LBP, GLCM, PRNU, Fourier/Wavelet analysis untuk authenticity verification

Performance Modes:
- FAST: Basic validation + LBP + GLCM (real-time friendly)
- THOROUGH: All analysis including Fourier/Wavelet (high accuracy)
- ADAPTIVE: Choose mode based on detection confidence and image size
"""
import cv2
import numpy as np
import os
import time
from core.config import get_ktp_template
from .template_manager import get_template_manager, get_adaptive_template, initialize_template_manager
from scipy import ndimage
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from scipy.fft import fft2, fftshift
import pywt

# === ADAPTIVE THRESHOLDS CONFIGURATION ===
class AuthenticityThresholds:
    """
    Adaptive thresholds berdasarkan image size, quality, dan mode detection
    TODO: Tune dengan dataset nyata KTP asli vs palsu
    """
    
    # Base thresholds (akan disesuaikan secara adaptif)
    BASE_LBP = 0.5        # Lowered from 0.6 - dataset tuning needed
    BASE_GLCM = 0.4       # Lowered from 0.5 - dataset tuning needed  
    BASE_PRNU = 0.3       # Lowered from 0.4 - often misleading for scanned KTP
    BASE_FOURIER = 0.4    # Lowered from 0.5 - resolution dependent
    
    # Minimum image size untuk reliable analysis
    MIN_WIDTH_FOR_FOURIER = 80   # Below this, skip Fourier analysis
    MIN_HEIGHT_FOR_FOURIER = 50
    MIN_WIDTH_FOR_PRNU = 60      # PRNU needs reasonable resolution
    MIN_HEIGHT_FOR_PRNU = 40
    
    # Performance mode settings
    FAST_MODE_TIMEOUT = 50        # milliseconds per detection
    THOROUGH_MODE_TIMEOUT = 200   # milliseconds per detection
    
    @staticmethod
    def get_adaptive_thresholds(image_size, template_confidence, mode='adaptive'):
        """
        Calculate adaptive thresholds based on image characteristics
        """
        w, h = image_size
        area = w * h
        
        # Size-based adjustments
        size_factor = min(area / 5000.0, 1.0)  # Normalize to 5000px baseline
        
        # Confidence-based adjustments (higher template confidence = more lenient)
        conf_factor = 0.8 + (template_confidence * 0.4)  # 0.8 to 1.2 range
        
        thresholds = {
            'lbp': max(AuthenticityThresholds.BASE_LBP * size_factor * conf_factor, 0.3),
            'glcm': max(AuthenticityThresholds.BASE_GLCM * size_factor * conf_factor, 0.25),
            'prnu': max(AuthenticityThresholds.BASE_PRNU * size_factor * conf_factor, 0.2),
            'fourier': max(AuthenticityThresholds.BASE_FOURIER * size_factor * conf_factor, 0.3),
            'min_checks': 4 if mode == 'fast' else 6  # Minimum checks to pass
        }
        
        return thresholds

# === PERFORMANCE MONITORING ===
class PerformanceMonitor:
    def __init__(self):
        self.analysis_times = {}
        self.total_detections = 0
        self.fast_mode_used = 0
        
    def log_analysis_time(self, analysis_type, duration):
        if analysis_type not in self.analysis_times:
            self.analysis_times[analysis_type] = []
        self.analysis_times[analysis_type].append(duration)
    
    def get_average_time(self, analysis_type):
        if analysis_type in self.analysis_times:
            return np.mean(self.analysis_times[analysis_type])
        return 0
    
    def should_use_fast_mode(self, current_load=None):
        """Determine if fast mode should be used based on performance"""
        if current_load and current_load > 0.8:  # High CPU load
            return True
        
        # If average analysis time is too high, switch to fast mode
        avg_total = sum(self.get_average_time(t) for t in ['lbp', 'glcm', 'fourier', 'prnu'])
        return avg_total > 100  # milliseconds

# Global performance monitor
performance_monitor = PerformanceMonitor()

def detect_ktp_by_template_similarity(frame):
    """
    Enhanced template-based KTP detection dengan adaptive template selection
    Returns: List of detected KTP regions with confidence scores
    """
    try:
        # Initialize template manager if not done
        template_manager = get_template_manager()
        if template_manager is None:
            # Initialize with assets directory
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            assets_dir = os.path.join(base_dir, "assets")
            template_manager = initialize_template_manager(assets_dir)
            print(f"📁 Initialized template manager with {template_manager.get_template_info()['total_templates']} templates")
        
        # Get adaptive template based on frame characteristics
        template_info = get_adaptive_template(frame)
        if template_info is None:
            print("❌ No suitable template found!")
            return []
        
        template = template_info['template']
        template_type = template_info['type']
        selection_reason = template_info.get('selection_reason', 'unknown')
        
        # Get template dimensions
        template_h, template_w = template.shape[:2]
        frame_h, frame_w = frame.shape[:2]
        
        print(f"🔍 Adaptive template detection:")
        print(f"   Template: {template_type} ({template_w}x{template_h})")
        print(f"   Reason: {selection_reason}")
        print(f"   Blue ratio: {template_info['blue_ratio']:.3f}")
        print(f"   Frame: {frame_w}x{frame_h}")
        
        detections = []
        
        # Multi-scale template matching untuk berbagai ukuran KTP
        scales = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
        
        for scale in scales:
            # Resize template sesuai scale
            new_w = int(template_w * scale)
            new_h = int(template_h * scale)
            
            # Skip jika template lebih besar dari frame
            if new_w > frame_w or new_h > frame_h:
                continue
                
            resized_template = cv2.resize(template, (new_w, new_h))
            
            # Template matching dengan multiple methods
            detection = perform_multiscale_template_matching(frame, resized_template, scale)
            if detection:
                # Add template info to detection
                detection['template_type'] = template_type
                detection['template_blue_ratio'] = template_info['blue_ratio']
                detections.append(detection)
        
        # Filter dan rank detections berdasarkan confidence
        filtered_detections = filter_and_rank_detections(detections)
        
        print(f"🎯 Found {len(filtered_detections)} high-confidence KTP detections using {template_type} template")
        return filtered_detections
        
    except Exception as e:
        print(f"❌ Error in template-based detection: {str(e)}")
        return []


def perform_multiscale_template_matching(frame, template, scale):
    """
    Perform template matching dengan multiple methods dan preprocessing
    """
    try:
        # Convert both to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Preprocessing untuk meningkatkan matching
        frame_processed = preprocess_for_matching(frame_gray)
        template_processed = preprocess_for_matching(template_gray)
        
        # Multiple template matching methods
        methods = [
            cv2.TM_CCOEFF_NORMED,
            cv2.TM_CCORR_NORMED,
            cv2.TM_SQDIFF_NORMED
        ]
        
        best_confidence = 0
        best_location = None
        best_method = None
        
        for method in methods:
            result = cv2.matchTemplate(frame_processed, template_processed, method)
            
            if method == cv2.TM_SQDIFF_NORMED:
                # Untuk SQDIFF, nilai lebih kecil = lebih baik
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                confidence = 1 - min_val  # Invert untuk consistency
                location = min_loc
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                confidence = max_val
                location = max_loc
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_location = location
                best_method = method
        
        # Threshold confidence untuk menfilter false positives
        if best_confidence >= 0.6:  # High threshold untuk template similarity
            template_h, template_w = template.shape[:2]
            x, y = best_location
            
            # Validasi posisi
            if x + template_w <= frame.shape[1] and y + template_h <= frame.shape[0]:
                return {
                    'bbox': (x, y, template_w, template_h),
                    'confidence': best_confidence,
                    'scale': scale,
                    'method': best_method,
                    'area': template_w * template_h
                }
        
        return None
        
    except Exception as e:
        print(f"   ❌ Template matching error at scale {scale}: {str(e)}")
        return None


def preprocess_for_matching(image):
    """
    Preprocessing untuk meningkatkan template matching accuracy
    """
    # Gaussian blur untuk reduce noise
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    
    # Histogram equalization untuk normalize brightness
    equalized = cv2.equalizeHist(blurred)
    
    # Edge enhancement (optional)
    # edges = cv2.Canny(equalized, 50, 150)
    # combined = cv2.addWeighted(equalized, 0.7, edges, 0.3, 0)
    
    return equalized


def filter_and_rank_detections(detections):
    """
    Filter overlapping detections dan rank berdasarkan confidence
    """
    if not detections:
        return []
    
    # Sort by confidence (descending)
    sorted_detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
    
    # Non-maximum suppression untuk remove overlapping detections
    filtered = []
    
    for current in sorted_detections:
        is_duplicate = False
        current_bbox = current['bbox']
        
        for existing in filtered:
            existing_bbox = existing['bbox']
            
            # Calculate overlap
            overlap_ratio = calculate_bbox_overlap(current_bbox, existing_bbox)
            
            # Jika overlap > 50%, skip detection ini
            if overlap_ratio > 0.5:
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered.append(current)
    
    # Return top 3 detections
    return filtered[:3]


def calculate_bbox_overlap(bbox1, bbox2):
    """
    Calculate intersection over union (IoU) of two bounding boxes
    """
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    
    # Calculate intersection
    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1 + w1, x2 + w2)
    inter_y2 = min(y1 + h1, y2 + h2)
    
    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0
    
    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    
    # Calculate union
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area
    
    if union_area == 0:
        return 0.0
    
    return inter_area / union_area


def validate_ktp_detection(frame, detection, mode='adaptive'):
    """
    Validasi tambahan untuk memastikan detection adalah KTP asli
    Menggunakan advanced texture analysis untuk authenticity verification
    
    Mode options:
    - 'fast': Basic + LBP + GLCM only (real-time friendly)
    - 'thorough': All analysis including Fourier/Wavelet 
    - 'adaptive': Choose based on image size and performance
    """
    start_time = time.time() * 1000  # milliseconds
    
    try:
        bbox = detection['bbox']
        x, y, w, h = bbox
        
        # Extract region
        ktp_region = frame[y:y+h, x:x+w]
        
        if ktp_region.size == 0:
            return False, 0.0
        
        # Determine analysis mode
        if mode == 'adaptive':
            if performance_monitor.should_use_fast_mode():
                mode = 'fast'
                performance_monitor.fast_mode_used += 1
            elif w < AuthenticityThresholds.MIN_WIDTH_FOR_FOURIER or h < AuthenticityThresholds.MIN_HEIGHT_FOR_FOURIER:
                mode = 'fast'
            else:
                mode = 'thorough'
        
        print(f"   🔧 Using {mode.upper()} analysis mode")
        
        # Get adaptive thresholds
        thresholds = AuthenticityThresholds.get_adaptive_thresholds(
            (w, h), detection['confidence'], mode
        )
        
        # Basic validation checks
        validation_score = 0
        total_checks = 5 if mode == 'fast' else 9
        
        # Check 1: Aspect ratio validation
        aspect_ratio = w / h if h > 0 else 0
        if 1.4 <= aspect_ratio <= 2.0:  # KTP aspect ratio range
            validation_score += 1
            print(f"   ✅ Aspect ratio valid: {aspect_ratio:.2f}")
        else:
            print(f"   ❌ Invalid aspect ratio: {aspect_ratio:.2f}")
        
        # Check 2: Size validation (not too small or too large)
        frame_area = frame.shape[0] * frame.shape[1]
        region_area = w * h
        area_ratio = region_area / frame_area
        
        if 0.05 <= area_ratio <= 0.8:  # 5% to 80% of frame
            validation_score += 1
            print(f"   ✅ Size valid: {area_ratio:.3f} of frame")
        else:
            print(f"   ❌ Invalid size: {area_ratio:.3f} of frame")
        
        # Check 3: Edge density (KTP should have good edge definition)
        gray_region = cv2.cvtColor(ktp_region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_region, 50, 150)
        edge_density = np.sum(edges > 0) / (w * h)
        
        if 0.05 <= edge_density <= 0.25:  # Reasonable edge density
            validation_score += 1
            print(f"   ✅ Edge density valid: {edge_density:.3f}")
        else:
            print(f"   ❌ Invalid edge density: {edge_density:.3f}")
        
        # Check 4: Color variance (KTP should have color variation)
        color_std = np.std(ktp_region.reshape(-1, 3), axis=0)
        avg_std = np.mean(color_std)
        
        if avg_std >= 15:  # Sufficient color variation
            validation_score += 1
            print(f"   ✅ Color variance valid: {avg_std:.1f}")
        else:
            print(f"   ❌ Low color variance: {avg_std:.1f}")
        
        # Check 5: Template confidence threshold
        if detection['confidence'] >= 0.65:
            validation_score += 1
            print(f"   ✅ High template confidence: {detection['confidence']:.3f}")
        else:
            print(f"   ⚠️ Lower template confidence: {detection['confidence']:.3f}")
        
        # === ADVANCED TEXTURE ANALYSIS (Mode-dependent) ===
        
        # Always perform LBP and GLCM (fast and reliable)
        if mode in ['fast', 'thorough']:
            # Check 6: LBP (Local Binary Pattern) Analysis
            lbp_start = time.time() * 1000
            lbp_authenticity = analyze_lbp_texture(gray_region)
            lbp_time = time.time() * 1000 - lbp_start
            performance_monitor.log_analysis_time('lbp', lbp_time)
            
            if lbp_authenticity >= thresholds['lbp']:
                validation_score += 1
                print(f"   ✅ LBP texture authentic: {lbp_authenticity:.3f} (threshold: {thresholds['lbp']:.3f})")
            else:
                print(f"   ❌ LBP texture suspicious: {lbp_authenticity:.3f} (threshold: {thresholds['lbp']:.3f})")
            
            # Check 7: GLCM (Gray Level Co-occurrence Matrix) Analysis
            glcm_start = time.time() * 1000
            glcm_authenticity = analyze_glcm_properties(gray_region)
            glcm_time = time.time() * 1000 - glcm_start
            performance_monitor.log_analysis_time('glcm', glcm_time)
            
            if glcm_authenticity >= thresholds['glcm']:
                validation_score += 1
                print(f"   ✅ GLCM properties authentic: {glcm_authenticity:.3f} (threshold: {thresholds['glcm']:.3f})")
            else:
                print(f"   ❌ GLCM properties suspicious: {glcm_authenticity:.3f} (threshold: {thresholds['glcm']:.3f})")
        
        # Thorough mode: Add PRNU and Frequency analysis
        if mode == 'thorough':
            # Check 8: PRNU Analysis (only if image is large enough and likely from camera)
            if w >= AuthenticityThresholds.MIN_WIDTH_FOR_PRNU and h >= AuthenticityThresholds.MIN_HEIGHT_FOR_PRNU:
                prnu_start = time.time() * 1000
                prnu_authenticity = analyze_prnu_pattern(gray_region)
                prnu_time = time.time() * 1000 - prnu_start
                performance_monitor.log_analysis_time('prnu', prnu_time)
                
                if prnu_authenticity >= thresholds['prnu']:
                    validation_score += 1
                    print(f"   ✅ PRNU pattern authentic: {prnu_authenticity:.3f} (threshold: {thresholds['prnu']:.3f})")
                else:
                    print(f"   ⚠️ PRNU pattern suspicious: {prnu_authenticity:.3f} (may be scanned/printed)")
            else:
                print(f"   ⏭️ PRNU analysis skipped (image too small: {w}x{h})")
                validation_score += 0.5  # Partial credit for skipped analysis
            
            # Check 9: Frequency Domain Analysis (only if image is large enough)
            if w >= AuthenticityThresholds.MIN_WIDTH_FOR_FOURIER and h >= AuthenticityThresholds.MIN_HEIGHT_FOR_FOURIER:
                freq_start = time.time() * 1000
                freq_authenticity = analyze_frequency_domain(gray_region)
                freq_time = time.time() * 1000 - freq_start
                performance_monitor.log_analysis_time('fourier', freq_time)
                
                if freq_authenticity >= thresholds['fourier']:
                    validation_score += 1
                    print(f"   ✅ Frequency analysis authentic: {freq_authenticity:.3f} (threshold: {thresholds['fourier']:.3f})")
                else:
                    print(f"   ⚠️ Frequency analysis suspicious: {freq_authenticity:.3f} (may be printed/copied)")
            else:
                print(f"   ⏭️ Frequency analysis skipped (image too small: {w}x{h})")
                validation_score += 0.5  # Partial credit for skipped analysis
        
        # Calculate final validation score
        final_score = validation_score / total_checks
        is_valid = validation_score >= thresholds['min_checks']
        
        # Performance monitoring
        total_time = time.time() * 1000 - start_time
        performance_monitor.total_detections += 1
        
        print(f"   📊 {mode.upper()} Validation: {validation_score:.1f}/{total_checks} checks passed")
        print(f"   ⏱️ Analysis time: {total_time:.1f}ms, final score: {final_score:.2f}")
        
        # Timeout protection
        timeout_limit = AuthenticityThresholds.FAST_MODE_TIMEOUT if mode == 'fast' else AuthenticityThresholds.THOROUGH_MODE_TIMEOUT
        if total_time > timeout_limit:
            print(f"   ⚠️ Analysis timeout ({total_time:.1f}ms > {timeout_limit}ms)")
        
        return is_valid, final_score
        
    except Exception as e:
        print(f"   ❌ Validation error: {str(e)}")
        return False, 0.0


def analyze_lbp_texture(gray_image):
    """
    LBP (Local Binary Pattern) Analysis untuk mendeteksi pola tekstur permukaan KTP
    KTP asli memiliki tekstur khusus yang berbeda dari foto/fotokopi
    """
    try:
        if gray_image.size == 0:
            return 0.0
        
        # Resize untuk konsistensi jika terlalu kecil
        if gray_image.shape[0] < 50 or gray_image.shape[1] < 50:
            gray_image = cv2.resize(gray_image, (100, 60))
        
        # LBP parameters
        radius = 2
        n_points = 8 * radius
        
        # Compute LBP
        lbp = local_binary_pattern(gray_image, n_points, radius, method='uniform')
        
        # Calculate histogram of LBP patterns
        hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-7)  # Normalize
        
        # KTP asli characteristics:
        # - Uniform patterns should dominate (high uniformity)
        # - Specific texture patterns from security features
        uniform_patterns = hist[:-2]  # Exclude non-uniform patterns
        uniformity_ratio = np.sum(uniform_patterns)
        
        # Entropy measure (lower entropy = more structured texture = more likely authentic)
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        normalized_entropy = min(entropy / 4.0, 1.0)  # Normalize to 0-1
        
        # Variance in LBP (authentic documents have consistent texture)
        lbp_variance = np.var(lbp)
        normalized_variance = min(lbp_variance / 1000.0, 1.0)
        
        # Combined authenticity score
        # High uniformity + moderate entropy + reasonable variance = authentic
        authenticity_score = (uniformity_ratio * 0.5 + 
                            (1 - normalized_entropy) * 0.3 + 
                            normalized_variance * 0.2)
        
        return min(authenticity_score, 1.0)
        
    except Exception as e:
        print(f"      LBP analysis error: {str(e)}")
        return 0.0


def analyze_glcm_properties(gray_image):
    """
    GLCM (Gray Level Co-occurrence Matrix) Analysis
    Mengukur distribusi kontras, homogenitas, dan energy dalam texture
    """
    try:
        if gray_image.size == 0:
            return 0.0
        
        # Resize dan normalize untuk GLCM
        if gray_image.shape[0] < 30 or gray_image.shape[1] < 30:
            gray_image = cv2.resize(gray_image, (60, 40))
        
        # Reduce gray levels untuk computational efficiency
        gray_image = (gray_image / 32).astype(np.uint8)  # Reduce to 8 levels
        
        # GLCM parameters - multiple directions untuk robustness
        distances = [1, 2]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        contrast_values = []
        homogeneity_values = []
        energy_values = []
        correlation_values = []
        
        for distance in distances:
            for angle in angles:
                try:
                    # Calculate GLCM
                    glcm = graycomatrix(gray_image, [distance], [angle], 
                                     levels=8, symmetric=True, normed=True)
                    
                    # Extract texture properties
                    contrast = graycoprops(glcm, 'contrast')[0, 0]
                    homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
                    energy = graycoprops(glcm, 'energy')[0, 0]
                    correlation = graycoprops(glcm, 'correlation')[0, 0]
                    
                    contrast_values.append(contrast)
                    homogeneity_values.append(homogeneity)
                    energy_values.append(energy)
                    correlation_values.append(correlation)
                    
                except:
                    continue
        
        if not contrast_values:
            return 0.0
        
        # Average values across all directions
        avg_contrast = np.mean(contrast_values)
        avg_homogeneity = np.mean(homogeneity_values)
        avg_energy = np.mean(energy_values)
        avg_correlation = np.mean(correlation_values)
        
        # KTP asli characteristics:
        # - Moderate contrast (not too flat, not too noisy)
        # - High homogeneity (consistent texture)
        # - Reasonable energy (structured patterns)
        # - Good correlation (organized texture)
        
        # Normalize values to 0-1 and calculate authenticity
        contrast_score = 1.0 - min(avg_contrast / 10.0, 1.0)  # Lower contrast is better
        homogeneity_score = min(avg_homogeneity * 2.0, 1.0)   # Higher homogeneity is better
        energy_score = min(avg_energy * 5.0, 1.0)             # Reasonable energy
        correlation_score = min(avg_correlation + 0.5, 1.0)   # Good correlation
        
        # Weighted combination
        authenticity_score = (contrast_score * 0.3 + 
                            homogeneity_score * 0.3 + 
                            energy_score * 0.2 + 
                            correlation_score * 0.2)
        
        return authenticity_score
        
    except Exception as e:
        print(f"      GLCM analysis error: {str(e)}")
        return 0.0


def analyze_prnu_pattern(gray_image):
    """
    PRNU (Photo Response Non-Uniformity) Analysis
    WARNING: PRNU lebih cocok untuk foto dari kamera digital.
    Untuk scanned/printed KTP, hasil bisa misleading!
    
    Returns: Authenticity score, tapi dengan catatan khusus untuk scanned images
    """
    try:
        if gray_image.size == 0:
            return 0.0
        
        # Resize untuk consistency
        if gray_image.shape[0] < 40 or gray_image.shape[1] < 40:
            gray_image = cv2.resize(gray_image, (80, 50))
        
        # Convert to float
        image_float = gray_image.astype(np.float32)
        
        # Denoising untuk isolate PRNU pattern
        # Gaussian filter untuk estimate noise-free version
        denoised = cv2.GaussianBlur(image_float, (5, 5), 1.0)
        
        # PRNU pattern = original - denoised
        prnu_pattern = image_float - denoised
        
        # Analyze PRNU characteristics
        # 1. Variance analysis - sensor noise should have specific characteristics
        prnu_variance = np.var(prnu_pattern)
        
        # 2. Distribution analysis - authentic sensor noise follows specific distribution
        prnu_std = np.std(prnu_pattern)
        prnu_mean = np.abs(np.mean(prnu_pattern))
        
        # 3. Spatial frequency analysis of PRNU
        prnu_fft = np.abs(fft2(prnu_pattern))
        prnu_fft_center = fftshift(prnu_fft)
        
        # High frequency energy ratio (sensor noise has more high freq components)
        h, w = prnu_fft_center.shape
        center_h, center_w = h//2, w//2
        
        # High frequency region (outer ring)
        mask_high = np.zeros((h, w))
        y, x = np.ogrid[:h, :w]
        mask_high[((x - center_w)**2 + (y - center_h)**2) > (min(h,w)//4)**2] = 1
        
        high_freq_energy = np.sum(prnu_fft_center * mask_high)
        total_energy = np.sum(prnu_fft_center)
        high_freq_ratio = high_freq_energy / (total_energy + 1e-7)
        
        # ADJUSTED SCORING for scanned/printed documents
        # Lower expectations because PRNU from camera sensors won't be present
        
        # For scanned documents, look for:
        # - Some variance (not completely flat)
        # - But not too much noise (which would indicate poor scanning)
        variance_score = min(prnu_variance / 50.0, 1.0) if prnu_variance > 2 else 0  # Lowered threshold
        mean_score = max(0, 1.0 - prnu_mean / 15.0)  # More lenient
        frequency_score = min(high_freq_ratio * 2.0, 1.0)  # Reduced weight
        
        # Combined authenticity score (more forgiving for scanned documents)
        authenticity_score = (variance_score * 0.5 + 
                            mean_score * 0.3 + 
                            frequency_score * 0.2)
        
        # Apply penalty if image is likely scanned (very clean/uniform)
        if prnu_variance < 1.0 and prnu_mean < 2.0:
            # This looks like a scanned image - apply different criteria
            authenticity_score = max(authenticity_score, 0.4)  # Give benefit of doubt
        
        return authenticity_score
        
    except Exception as e:
        print(f"      PRNU analysis error: {str(e)}")
        return 0.3  # Default reasonable score for scanned images


def analyze_frequency_domain(gray_image):
    """
    Frequency Domain Analysis menggunakan Fourier dan Wavelet Transform
    WARNING: Hasil sangat dipengaruhi resolusi! 
    Jika KTP terlalu kecil di kamera, analisis frekuensi jadi noise.
    
    Minimum recommended size: 64x40 pixels
    """
    try:
        if gray_image.size == 0:
            return 0.0
        
        h, w = gray_image.shape
        
        # Resolution check - skip if too small for reliable frequency analysis
        if w < 64 or h < 40:
            print(f"        Warning: Image too small ({w}x{h}) for reliable frequency analysis")
            return 0.5  # Neutral score rather than failing
        
        # Resize untuk consistency but preserve aspect ratio
        target_size = 128
        scale = min(target_size / w, target_size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        if new_w != w or new_h != h:
            gray_image = cv2.resize(gray_image, (new_w, new_h))
        
        # === FOURIER ANALYSIS ===
        fourier_score = analyze_fourier_spectrum(gray_image)
        
        # === WAVELET ANALYSIS ===
        wavelet_score = analyze_wavelet_coefficients(gray_image)
        
        # Combined frequency domain authenticity
        # Weight more towards fourier for smaller images
        if new_w * new_h < 5000:
            frequency_authenticity = (fourier_score * 0.7 + wavelet_score * 0.3)
        else:
            frequency_authenticity = (fourier_score * 0.6 + wavelet_score * 0.4)
        
        return frequency_authenticity
        
    except Exception as e:
        print(f"      Frequency analysis error: {str(e)}")
        return 0.4  # Default reasonable score for small/problematic images


def analyze_fourier_spectrum(gray_image):
    """
    Analisis spektrum Fourier untuk mendeteksi pola printing/scanning
    """
    try:
        # FFT analysis
        f_transform = fft2(gray_image)
        f_shift = fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        log_spectrum = np.log(magnitude_spectrum + 1)
        
        h, w = log_spectrum.shape
        center_h, center_w = h//2, w//2
        
        # Analyze frequency distribution
        # 1. Low frequency energy (DC and near-DC components)
        mask_low = np.zeros((h, w))
        y, x = np.ogrid[:h, :w]
        low_freq_radius = min(h, w) // 8
        mask_low[((x - center_w)**2 + (y - center_h)**2) <= low_freq_radius**2] = 1
        
        low_freq_energy = np.sum(log_spectrum * mask_low)
        
        # 2. Mid frequency energy
        mask_mid = np.zeros((h, w))
        mid_freq_radius = min(h, w) // 4
        mask_mid[((x - center_w)**2 + (y - center_h)**2) <= mid_freq_radius**2] = 1
        mask_mid = mask_mid - mask_low  # Ring shape
        
        mid_freq_energy = np.sum(log_spectrum * mask_mid)
        
        # 3. High frequency energy
        mask_high = np.ones((h, w)) - (mask_low + mask_mid)
        high_freq_energy = np.sum(log_spectrum * mask_high)
        
        total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
        
        if total_energy == 0:
            return 0.0
        
        # Ratio analysis
        low_ratio = low_freq_energy / total_energy
        mid_ratio = mid_freq_energy / total_energy
        high_ratio = high_freq_energy / total_energy
        
        # Authentic documents have balanced frequency distribution
        # Printed/scanned documents often have artificial frequency patterns
        
        # Look for natural frequency distribution
        # Too much low freq = blurry/low quality
        # Too much high freq = artificial sharpening/noise
        balance_score = 1.0 - abs(0.4 - low_ratio) - abs(0.4 - mid_ratio) - abs(0.2 - high_ratio)
        balance_score = max(0, balance_score * 2.5)  # Amplify and clamp
        
        # Check for printing artifacts (regular patterns in frequency domain)
        # Calculate variance in different frequency bands
        low_variance = np.var(log_spectrum * mask_low) if np.sum(mask_low) > 0 else 0
        mid_variance = np.var(log_spectrum * mask_mid) if np.sum(mask_mid) > 0 else 0
        
        # Higher variance = more natural, lower variance = more artificial
        variance_score = min((low_variance + mid_variance) / 20.0, 1.0)
        
        return (balance_score * 0.7 + variance_score * 0.3)
        
    except Exception as e:
        print(f"        Fourier analysis error: {str(e)}")
        return 0.0


def analyze_wavelet_coefficients(gray_image):
    """
    Analisis koefisien Wavelet untuk mendeteksi karakteristik autentik
    """
    try:
        # Wavelet decomposition
        coeffs = pywt.dwt2(gray_image, 'db4')
        cA, (cH, cV, cD) = coeffs
        
        # Analyze coefficients statistics
        # 1. Approximation coefficients (low-frequency content)
        cA_energy = np.sum(cA**2)
        cA_variance = np.var(cA)
        
        # 2. Detail coefficients (high-frequency content)
        cH_energy = np.sum(cH**2)
        cV_energy = np.sum(cV**2)
        cD_energy = np.sum(cD**2)
        
        detail_energy = cH_energy + cV_energy + cD_energy
        total_energy = cA_energy + detail_energy
        
        if total_energy == 0:
            return 0.0
        
        # Energy ratio analysis
        detail_ratio = detail_energy / total_energy
        
        # Coefficient distribution analysis
        # Authentic images have specific coefficient distributions
        cH_kurtosis = calculate_kurtosis(cH.flatten())
        cV_kurtosis = calculate_kurtosis(cV.flatten())
        cD_kurtosis = calculate_kurtosis(cD.flatten())
        
        avg_kurtosis = (cH_kurtosis + cV_kurtosis + cD_kurtosis) / 3
        
        # Scoring
        # Natural images have:
        # - Balanced energy distribution
        # - Specific kurtosis values (not too peaked, not too flat)
        energy_score = min(detail_ratio * 4.0, 1.0) if detail_ratio > 0.1 else 0
        kurtosis_score = max(0, 1.0 - abs(avg_kurtosis - 3.0) / 10.0)  # Normal distribution has kurtosis ~3
        
        return (energy_score * 0.6 + kurtosis_score * 0.4)
        
    except Exception as e:
        print(f"        Wavelet analysis error: {str(e)}")
        return 0.0


def calculate_kurtosis(data):
    """Calculate kurtosis of data array"""
    try:
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        normalized = (data - mean) / std
        kurtosis = np.mean(normalized**4)
        return kurtosis
    except:
        return 0


# Main detection function yang akan dipanggil dari sistem utama
def detect_ktp_template_based(frame, performance_mode='adaptive'):
    """
    Main function untuk deteksi KTP berdasarkan template similarity
    
    Performance modes:
    - 'fast': Quick analysis (LBP + GLCM only)
    - 'thorough': Full analysis including Fourier/Wavelet  
    - 'adaptive': Auto-choose based on system performance and image characteristics
    
    Returns: List of validated KTP detections
    """
    print(f"🎯 Starting template-based KTP detection (mode: {performance_mode})...")
    
    # Step 1: Template matching
    raw_detections = detect_ktp_by_template_similarity(frame)
    
    if not raw_detections:
        print("❌ No template matches found")
        return []
    
    # Step 2: Validate each detection with performance monitoring
    validated_detections = []
    
    for i, detection in enumerate(raw_detections):
        print(f"🔍 Validating detection {i+1}/{len(raw_detections)}...")
        
        is_valid, validation_score = validate_ktp_detection(frame, detection, performance_mode)
        
        if is_valid:
            # Combine template confidence with validation score
            combined_confidence = (detection['confidence'] * 0.6) + (validation_score * 0.4)
            
            detection['validation_score'] = validation_score
            detection['combined_confidence'] = combined_confidence
            detection['analysis_mode'] = performance_mode
            
            validated_detections.append(detection)
            print(f"   ✅ Detection validated! Combined confidence: {combined_confidence:.3f}")
        else:
            print(f"   ❌ Detection rejected (validation score: {validation_score:.2f})")
    
    # Sort by combined confidence
    validated_detections.sort(key=lambda x: x['combined_confidence'], reverse=True)
    
    # Performance statistics
    if performance_monitor.total_detections > 0:
        fast_mode_percentage = (performance_monitor.fast_mode_used / performance_monitor.total_detections) * 100
        print(f"📈 Performance stats: {fast_mode_percentage:.1f}% fast mode usage")
        
        avg_times = {
            'LBP': performance_monitor.get_average_time('lbp'),
            'GLCM': performance_monitor.get_average_time('glcm'),
            'PRNU': performance_monitor.get_average_time('prnu'),
            'Fourier': performance_monitor.get_average_time('fourier')
        }
        
        for analysis, avg_time in avg_times.items():
            if avg_time > 0:
                print(f"    ⏱️ {analysis}: {avg_time:.1f}ms avg")
    
    print(f"🎯 Template-based detection complete: {len(validated_detections)} valid KTP found")
    
    return validated_detections


# === CONFIGURATION AND UTILITIES ===

def configure_authenticity_thresholds(lbp=None, glcm=None, prnu=None, fourier=None):
    """
    Configure custom thresholds - TODO: Load from trained model or config file
    """
    if lbp is not None:
        AuthenticityThresholds.BASE_LBP = lbp
    if glcm is not None:
        AuthenticityThresholds.BASE_GLCM = glcm  
    if prnu is not None:
        AuthenticityThresholds.BASE_PRNU = prnu
    if fourier is not None:
        AuthenticityThresholds.BASE_FOURIER = fourier
    
    print(f"📊 Thresholds updated: LBP={AuthenticityThresholds.BASE_LBP}, "
          f"GLCM={AuthenticityThresholds.BASE_GLCM}, "
          f"PRNU={AuthenticityThresholds.BASE_PRNU}, "
          f"Fourier={AuthenticityThresholds.BASE_FOURIER}")


def get_performance_statistics():
    """
    Get detailed performance statistics for system tuning
    """
    return {
        'total_detections': performance_monitor.total_detections,
        'fast_mode_usage': performance_monitor.fast_mode_used,
        'average_times': {
            'lbp': performance_monitor.get_average_time('lbp'),
            'glcm': performance_monitor.get_average_time('glcm'), 
            'prnu': performance_monitor.get_average_time('prnu'),
            'fourier': performance_monitor.get_average_time('fourier')
        }
    }


def reset_performance_monitor():
    """Reset performance statistics"""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    print("📊 Performance monitor reset")
