"""
KTP Detection Module - 2-Layer Detection System
"""
import cv2
import numpy as np
import os
from core.config import get_ktp_template

def detect_ktp_candidates_by_color_and_shape(frame):
    """
    Layer 1: Deteksi kandidat KTP berdasarkan warna biru dan bentuk persegi panjang
    Returns: List of candidate regions [(x, y, w, h, area, blue_ratio), ...]
    """
    h, w, _ = frame.shape
    candidates = []
    
    # Deteksi KTP berdasarkan warna biru dan bentuk persegi panjang
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Range warna biru header KTP yang lebih luas untuk menangkap variasi
    lower_blue = np.array([90, 40, 40])    # Lebih luas: cyan ke biru tua
    upper_blue = np.array([140, 255, 255]) # Termasuk biru terang
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Cari contour pada mask biru
    contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Threshold minimal area KTP (lebih kecil untuk webcam)
        if area > 0.008 * h * w:  # 0.8% dari area frame (lebih realistis)
            x, y, w2, h2 = cv2.boundingRect(cnt)
            aspect = w2 / h2 if h2 > 0 else 0
            # Validasi rasio aspect untuk KTP (lebih luas untuk berbagai sudut)
            if 1.2 < aspect < 2.8:  # Range lebih luas untuk capture angle
                # Validasi tambahan: cek apakah area biru cukup besar dalam bounding box
                roi_mask = mask_blue[y:y+h2, x:x+w2]
                blue_pixels = cv2.countNonZero(roi_mask)
                total_pixels = w2 * h2
                blue_ratio = blue_pixels / total_pixels if total_pixels > 0 else 0
                
                # Threshold blue ratio yang lebih longgar
                if blue_ratio >= 0.15:  # Minimal 15% area biru (lebih realistis)
                    candidates.append((x, y, w2, h2, area, blue_ratio))
                    print(f"🔍 KTP Candidate found: {w2}x{h2}, aspect={aspect:.2f}, blue_ratio={blue_ratio:.2f}")
                else:
                    print(f"🔸 Rejected candidate: blue_ratio={blue_ratio:.2f} < 0.15")
            else:
                print(f"🔸 Rejected candidate: aspect={aspect:.2f} not in range [1.2, 2.8]")
        else:
            print(f"🔸 Rejected candidate: area={area} < {0.008 * h * w:.0f}")
    
    print(f"🔍 Layer 1: Found {len(candidates)} candidates total")
    
    # Fallback: jika tidak ada kandidat biru, coba deteksi persegi panjang umum
    if len(candidates) == 0:
        print("🔄 No blue candidates found, trying fallback detection...")
        candidates = detect_rectangular_candidates_fallback(frame)
        print(f"🔄 Fallback found {len(candidates)} rectangular candidates")
    
    return candidates


def detect_rectangular_candidates_fallback(frame):
    """
    Fallback detection: cari objek persegi panjang dengan ukuran wajar 
    tanpa mengandalkan warna biru (untuk KTP dengan warna pudar/berbeda)
    """
    h, w, _ = frame.shape
    candidates = []
    
    # Convert ke grayscale dan deteksi edge
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Morphological operations untuk menyatukan edge
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Cari contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Area minimal untuk objek yang mungkin KTP
        if area > 0.005 * h * w:  # 0.5% dari frame
            # Approximasi bentuk
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            # Cek jika bentuknya mendekati persegi panjang (4-8 titik)
            if 4 <= len(approx) <= 8:
                x, y, w2, h2 = cv2.boundingRect(cnt)
                aspect = w2 / h2 if h2 > 0 else 0
                
                # Aspect ratio yang wajar untuk dokumen
                if 1.0 < aspect < 3.0:
                    # Hitung fill ratio (seberapa penuh contour mengisi bounding box)
                    contour_area = cv2.contourArea(cnt)
                    bbox_area = w2 * h2
                    fill_ratio = contour_area / bbox_area if bbox_area > 0 else 0
                    
                    # Filter objek yang terlalu fragmentaris
                    if fill_ratio >= 0.7:  # Minimal 70% fill
                        # Fake blue_ratio untuk konsistensi dengan format kandidat
                        fake_blue_ratio = 0.1  # Tandai sebagai fallback
                        candidates.append((x, y, w2, h2, area, fake_blue_ratio))
                        print(f"🔄 Fallback candidate: {w2}x{h2}, aspect={aspect:.2f}, fill={fill_ratio:.2f}")
    
    return candidates


def verify_ktp_candidate_by_template(frame, candidate_region):
    """
    Layer 2: Verifikasi kandidat KTP dengan Pattern Matching untuk fitur KTP asli
    """
    try:
        ktp_template = get_ktp_template()
        
        if ktp_template is None:
            print(f"   ❌ KTP_TEMPLATE is None! Template not loaded properly.")
            return 0.0, None
        
        x, y, w, h, area, blue_ratio = candidate_region
        
        # Validate coordinates
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            print(f"   ❌ Invalid candidate region: ({x},{y}) size {w}x{h}")
            return 0.0, None
            
        # Ensure coordinates are within frame bounds
        frame_height, frame_width = frame.shape[:2]
        if x + w > frame_width or y + h > frame_height:
            print(f"   ❌ Candidate region out of bounds: ({x},{y}) size {w}x{h} vs frame {frame_width}x{frame_height}")
            return 0.0, None
        
        candidate_crop = frame[y:y+h, x:x+w]
        
        if candidate_crop.size == 0:
            print(f"   ❌ Empty candidate crop at ({x},{y}) size {w}x{h}")
            return 0.0, None
        
        print(f"   🔍 Pattern matching candidate: {w}x{h} at ({x},{y}) with blue_ratio={blue_ratio:.2f}")
        
        # Pattern Recognition untuk KTP Indonesia
        pattern_score = 0
        total_patterns = 7  # Tambah 1 untuk watermark detection
        
        # Pattern 1: Blue Header Region Detection
        try:
            header_score = detect_blue_header_pattern(candidate_crop)
            if header_score >= 0.6:
                pattern_score += 1
                print(f"   ✅ Pattern 1: Blue header detected ({header_score:.2f})")
            elif header_score >= 0.4:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 1: Weak blue header ({header_score:.2f})")
            else:
                print(f"   ❌ Pattern 1: No blue header ({header_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 1 error: {str(e)}")
            header_score = 0
        
        # Pattern 2: Text Region Structure
        try:
            text_score = detect_text_regions(candidate_crop)
            if text_score >= 0.5:
                pattern_score += 1
                print(f"   ✅ Pattern 2: Text regions found ({text_score:.2f})")
            elif text_score >= 0.3:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 2: Some text regions ({text_score:.2f})")
            else:
                print(f"   ❌ Pattern 2: No text structure ({text_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 2 error: {str(e)}")
            text_score = 0
        
        # Pattern 3: Photo Area Detection
        try:
            photo_score = detect_photo_area(candidate_crop)
            if photo_score >= 0.4:
                pattern_score += 1
                print(f"   ✅ Pattern 3: Photo area detected ({photo_score:.2f})")
            elif photo_score >= 0.25:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 3: Possible photo area ({photo_score:.2f})")
            else:
                print(f"   ❌ Pattern 3: No photo area ({photo_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 3 error: {str(e)}")
            photo_score = 0
        
        # Pattern 4: Background Gradient Analysis
        try:
            gradient_score = analyze_background_gradient(candidate_crop)
            if gradient_score >= 0.5:
                pattern_score += 1
                print(f"   ✅ Pattern 4: KTP gradient pattern ({gradient_score:.2f})")
            elif gradient_score >= 0.3:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 4: Weak gradient ({gradient_score:.2f})")
            else:
                print(f"   ❌ Pattern 4: No KTP gradient ({gradient_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 4 error: {str(e)}")
            gradient_score = 0
        
        # Pattern 5: Edge Density Analysis
        try:
            edge_score = analyze_edge_density(candidate_crop)
            if edge_score >= 0.4:
                pattern_score += 1
                print(f"   ✅ Pattern 5: Good edge density ({edge_score:.2f})")
            elif edge_score >= 0.25:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 5: Moderate edges ({edge_score:.2f})")
            else:
                print(f"   ❌ Pattern 5: Low edge density ({edge_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 5 error: {str(e)}")
            edge_score = 0
        
        # Pattern 6: Color Distribution Analysis
        try:
            color_score = analyze_color_distribution(candidate_crop)
            if color_score >= 0.5:
                pattern_score += 1
                print(f"   ✅ Pattern 6: KTP color pattern ({color_score:.2f})")
            elif color_score >= 0.3:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 6: Partial color match ({color_score:.2f})")
            else:
                print(f"   ❌ Pattern 6: Wrong color pattern ({color_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 6 error: {str(e)}")
            color_score = 0
        
        # Pattern 7: Watermark Detection (KTP security feature)
        try:
            watermark_score = detect_watermark_pattern(candidate_crop)
            if watermark_score >= 0.4:
                pattern_score += 1
                print(f"   ✅ Pattern 7: Watermark detected ({watermark_score:.2f})")
            elif watermark_score >= 0.25:
                pattern_score += 0.5
                print(f"   ⚡ Pattern 7: Possible watermark ({watermark_score:.2f})")
            else:
                print(f"   ❌ Pattern 7: No watermark ({watermark_score:.2f})")
        except Exception as e:
            print(f"   ❌ Pattern 7 error: {str(e)}")
            watermark_score = 0
        
        # Calculate final pattern confidence
        pattern_confidence = pattern_score / total_patterns
        print(f"   📊 Pattern Analysis: {pattern_score}/{total_patterns} = {pattern_confidence:.2f}")
        
        # Template matching sebagai validasi tambahan
        try:
            template_confidence = perform_template_matching(candidate_crop, ktp_template)
            print(f"   🔍 Template matching confidence: {template_confidence:.3f}")
        except Exception as e:
            print(f"   ❌ Template matching error: {str(e)}")
            template_confidence = 0.0
        
        # Combined scoring dengan emphasis pada pattern recognition
        final_confidence = (pattern_confidence * 0.7) + (template_confidence * 0.3)
        
        # Threshold yang lebih realistis dan fleksibel
        min_pattern_score = 0.35  # 2.5/7 patterns (lebih realistis untuk webcam)
        min_template_score = 0.35  # Lower template threshold untuk variasi lighting
        min_combined_score = 0.40  # More achievable combined score
        
        # Additional anti-fraud validation dengan logika yang lebih smart
        critical_patterns_passed = 0
        
        # Critical check 1: Blue header OR good template match OR fallback candidate
        if pattern_confidence >= 0.30 or template_confidence >= 0.45 or blue_ratio <= 0.15:  # Include fallback
            critical_patterns_passed += 1
            
        # Critical check 2: Combined score meets minimum OR strong pattern match
        if final_confidence >= 0.35 or pattern_confidence >= 0.40:  # Lower thresholds
            critical_patterns_passed += 1
        
        print(f"   🎯 Final scores - Pattern: {pattern_confidence:.2f}, Template: {template_confidence:.3f}, Combined: {final_confidence:.3f}")
        print(f"   🔒 Anti-fraud check: {critical_patterns_passed}/2 critical validations passed")
        
        # Simplified validation logic - either strong pattern OR good combined score
        validation_passed = False
        
        if pattern_confidence >= min_pattern_score and final_confidence >= min_combined_score:
            validation_passed = True
            print(f"   ✅ Passed via strong pattern + combined score")
        elif template_confidence >= 0.50 and critical_patterns_passed >= 1:
            validation_passed = True
            print(f"   ✅ Passed via strong template matching")
        elif final_confidence >= 0.45 and critical_patterns_passed >= 2:
            validation_passed = True
            print(f"   ✅ Passed via good overall score")
        elif blue_ratio <= 0.15 and pattern_confidence >= 0.25:  # Fallback candidates
            validation_passed = True
            print(f"   ✅ Passed via fallback detection with reasonable pattern")
        
        if validation_passed:
            print(f"   ✅ KTP PATTERN VERIFICATION PASSED!")
            return final_confidence, {
                'confidence': template_confidence,
                'pattern_score': pattern_confidence,
                'combined_score': final_confidence,
                'region': candidate_region
            }
        else:
            print(f"   ❌ KTP PATTERN VERIFICATION FAILED! (Critical checks: {critical_patterns_passed}/2)")
            return 0.0, None
            
    except Exception as e:
        print(f"   ❌ Critical error in KTP verification: {str(e)}")
        return 0.0, None


# Pattern Recognition Functions untuk KTP Indonesia
def detect_blue_header_pattern(candidate_crop):
    """Deteksi pola header biru khas KTP Indonesia - lebih fleksibel"""
    try:
        h, w = candidate_crop.shape[:2]
        # Fokus pada area header (bagian atas 30% dari KTP)
        header_region = candidate_crop[0:int(h*0.3), :]
        
        # Konversi ke HSV untuk deteksi biru
        hsv = cv2.cvtColor(header_region, cv2.COLOR_BGR2HSV)
        
        # Range biru untuk header KTP - lebih luas
        lower_blue = np.array([90, 30, 30])    # Lebih permisif
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Hitung persentase area biru di header
        blue_pixels = cv2.countNonZero(mask)
        total_pixels = header_region.shape[0] * header_region.shape[1]
        blue_ratio = blue_pixels / total_pixels if total_pixels > 0 else 0
        
        # Tambahkan deteksi warna alternatif (abu-abu gelap, hijau gelap)
        # Untuk KTP yang faded atau scan quality rendah
        lower_alt = np.array([0, 0, 40])      # Dark colors
        upper_alt = np.array([180, 100, 120]) # Low saturation
        mask_alt = cv2.inRange(hsv, lower_alt, upper_alt)
        
        alt_pixels = cv2.countNonZero(mask_alt)
        alt_ratio = alt_pixels / total_pixels if total_pixels > 0 else 0
        
        # Combined score: prioritas biru, fallback ke warna gelap
        final_score = max(blue_ratio * 2, alt_ratio * 1.2)
        
        return min(final_score, 1.0)  # Skalakan ke 0-1
    except:
        return 0.2  # Default score untuk stability


def detect_text_regions(candidate_crop):
    """Deteksi area teks yang khas pada KTP"""
    try:
        gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        
        # Edge detection untuk mencari area teks
        edges = cv2.Canny(gray, 50, 150)
        
        # Morphological operations untuk menghubungkan teks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Cari contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Hitung area teks vs total area
        text_area = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter untuk area yang mirip teks (rasio width/height)
            if 1.5 <= w/h <= 15 and cv2.contourArea(contour) > 100:
                text_area += cv2.contourArea(contour)
        
        total_area = candidate_crop.shape[0] * candidate_crop.shape[1]
        text_ratio = text_area / total_area
        
        return min(text_ratio * 10, 1.0)  # Skalakan ke 0-1
    except:
        return 0


def detect_photo_area(candidate_crop):
    """Deteksi area foto pada KTP - critical pattern"""
    try:
        h, w = candidate_crop.shape[:2]
        
        # Area foto biasanya di sebelah kiri (25% kiri, tengah vertikal)
        photo_x = 0
        photo_y = int(h * 0.25)
        photo_w = int(w * 0.25)  # Lebih kecil dan spesifik
        photo_h = int(h * 0.5)   # Area foto vertikal
        
        if photo_w < 10 or photo_h < 10:  # Too small
            return 0
            
        photo_region = candidate_crop[photo_y:photo_y+photo_h, photo_x:photo_x+photo_w]
        
        # Multiple checks for photo area
        gray = cv2.cvtColor(photo_region, cv2.COLOR_BGR2GRAY)
        
        # Check 1: Variance in pixel values (photos have high variance)
        variance = np.var(gray)
        variance_score = min(variance / 1500, 1.0)  # Lower threshold
        
        # Check 2: Edge density (photos have many edges)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = cv2.countNonZero(edges) / (photo_w * photo_h)
        edge_score = min(edge_density * 15, 1.0)
        
        # Check 3: Color variation (photos are not monochrome)
        color_std = np.std(photo_region, axis=(0,1))
        color_variation = np.mean(color_std) / 255.0
        color_score = min(color_variation * 8, 1.0)
        
        # Combined score - all must be reasonable for photo
        final_score = (variance_score + edge_score + color_score) / 3
        
        # Only pass if it really looks like a photo area
        return final_score if final_score >= 0.4 else 0
    except:
        return 0


def analyze_background_gradient(candidate_crop):
    """Analisis gradient background KTP asli - more flexible"""
    try:
        gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Skip area foto (kiri) dan fokus ke background area
        bg_region = gray[:, int(w*0.3):]  # Right 70% is background
        
        if bg_region.size == 0:
            return 0
        
        # Simplified gradient analysis for better stability
        
        # Check 1: Sobel gradient magnitude
        grad_x = cv2.Sobel(bg_region, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(bg_region, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        avg_magnitude = np.mean(magnitude)
        
        # More flexible scoring - KTP bisa memiliki berbagai tingkat gradient
        if 15 <= avg_magnitude <= 50:  # Relaxed range
            smoothness_score = 1.0
        elif 10 <= avg_magnitude <= 60:
            smoothness_score = 0.7
        else:
            smoothness_score = 0.3  # Still give some score
        
        # Check 2: Standard deviation (uniformity) - more lenient
        std_dev = np.std(bg_region)
        if std_dev <= 25:
            uniformity_score = 1.0
        elif std_dev <= 35:
            uniformity_score = 0.7
        else:
            uniformity_score = 0.4  # More forgiving
        
        # Combined score - at least one should be good
        final_score = max(smoothness_score, uniformity_score) * 0.7 + min(smoothness_score, uniformity_score) * 0.3
        
        # Return reasonable score even for imperfect backgrounds
        return max(final_score, 0.3)  # Minimum 0.3 to help stability
    except:
        return 0.3  # Default reasonable score


def analyze_edge_density(candidate_crop):
    """Analisis kepadatan edge untuk deteksi KTP asli - more stable"""
    try:
        gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Simplified edge analysis for better stability
        
        # Overall edge detection with adaptive threshold
        edges_overall = cv2.Canny(gray, 30, 100)  # Lower thresholds
        overall_density = cv2.countNonZero(edges_overall) / (h * w)
        
        # More flexible scoring for edge density
        if 0.04 <= overall_density <= 0.20:  # Wider acceptable range
            edge_score = 1.0
        elif 0.02 <= overall_density <= 0.25:  # Extended range
            edge_score = 0.7
        elif 0.01 <= overall_density <= 0.30:  # Very permissive
            edge_score = 0.5
        else:
            edge_score = 0.3  # Still give some score for stability
        
        # Bonus for having text-like regions (right side)
        if w > 50:  # Only if image is large enough
            text_region = gray[:, int(w*0.3):]  # Right 70%
            text_edges = cv2.Canny(text_region, 25, 80)
            text_density = cv2.countNonZero(text_edges) / (text_region.shape[0] * text_region.shape[1])
            
            # Bonus for text presence
            if text_density >= 0.05:
                edge_score = min(edge_score + 0.2, 1.0)
        
        return edge_score
    except:
        return 0.5  # Default reasonable score for stability


def analyze_color_distribution(candidate_crop):
    """Analisis distribusi warna khas KTP Indonesia - critical pattern"""
    try:
        # Multiple color space analysis
        hsv = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2HSV)
        bgr = candidate_crop.copy()
        h, w = candidate_crop.shape[:2]
        
        # Focus on header region for blue analysis (top 30%)
        header_region = hsv[:int(h*0.3), :]
        
        # Check 1: Blue dominance in header
        header_h = header_region[:,:,0]
        blue_pixels = np.sum((header_h >= 100) & (header_h <= 130))  # Blue hue range
        total_header_pixels = header_region.shape[0] * header_region.shape[1]
        blue_ratio = blue_pixels / total_header_pixels
        blue_score = min(blue_ratio * 3, 1.0)  # Amplify blue presence
        
        # Check 2: Overall saturation distribution
        s_channel = hsv[:,:,1]
        # KTP has moderate saturation (not too dull, not too vivid)
        good_sat_pixels = np.sum((s_channel >= 60) & (s_channel <= 180))
        sat_ratio = good_sat_pixels / (h * w)
        sat_score = min(sat_ratio * 1.5, 1.0)
        
        # Check 3: Value/brightness distribution
        v_channel = hsv[:,:,2]
        # Good visibility range
        good_bright_pixels = np.sum((v_channel >= 50) & (v_channel <= 220))
        bright_ratio = good_bright_pixels / (h * w)
        bright_score = min(bright_ratio * 1.2, 1.0)
        
        # Check 4: BGR channel balance (not too monochrome)
        b_std = np.std(bgr[:,:,0])
        g_std = np.std(bgr[:,:,1])
        r_std = np.std(bgr[:,:,2])
        color_variance = (b_std + g_std + r_std) / 3
        variance_score = min(color_variance / 30, 1.0)
        
        # Check 5: No extreme colors (filter out artificial/printed docs)
        extreme_pixels = np.sum((s_channel > 240) | (v_channel < 20) | (v_channel > 250))
        extreme_ratio = extreme_pixels / (h * w)
        natural_score = max(0, 1 - (extreme_ratio * 10))  # Penalize extreme colors
        
        # Weighted combination - blue header is critical
        final_score = (blue_score * 0.35 + sat_score * 0.2 + bright_score * 0.2 + 
                      variance_score * 0.15 + natural_score * 0.1)
        
        # High threshold for color authenticity
        return final_score if final_score >= 0.65 else 0
    except:
        return 0


def perform_template_matching(candidate_crop, template):
    """Template matching dengan preprocessing optimal"""
    try:
        # Preprocessing candidate
        gray_candidate = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        gray_candidate = cv2.GaussianBlur(gray_candidate, (3, 3), 0)
        gray_candidate = cv2.equalizeHist(gray_candidate)
        
        # Preprocessing template
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.GaussianBlur(gray_template, (3, 3), 0)
        gray_template = cv2.equalizeHist(gray_template)
        
        # Resize template untuk match candidate
        h, w = gray_candidate.shape
        template_resized = cv2.resize(gray_template, (w, h))
        
        # Multiple template matching methods
        result1 = cv2.matchTemplate(gray_candidate, template_resized, cv2.TM_CCOEFF_NORMED)
        result2 = cv2.matchTemplate(gray_candidate, template_resized, cv2.TM_CCORR_NORMED)
        
        # Ambil confidence terbaik
        _, max_val1, _, _ = cv2.minMaxLoc(result1)
        _, max_val2, _, _ = cv2.minMaxLoc(result2)
        
        return max(max_val1, max_val2)
    except:
        return 0


def detect_watermark_pattern(candidate_crop):
    """
    Deteksi watermark KTP Indonesia menggunakan pattern analysis
    Watermark KTP memiliki pola subtle yang berulang dengan opacity rendah
    """
    try:
        h, w = candidate_crop.shape[:2]
        
        # Convert ke grayscale untuk analisis watermark
        gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        
        # Preprocessing untuk enhance watermark pattern
        # High-pass filter untuk menonjolkan detail halus
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        high_pass = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
        
        # Adaptive histogram equalization untuk enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(high_pass)
        
        # Deteksi edge untuk pattern analysis
        edges = cv2.Canny(enhanced, 20, 60)
        
        # Check 1: Distribusi edge yang merata (karakteristik watermark)
        # Bagi gambar jadi 4 kuadran dan hitung edge density
        h_mid, w_mid = h//2, w//2
        quadrants = [
            edges[0:h_mid, 0:w_mid],
            edges[0:h_mid, w_mid:w],
            edges[h_mid:h, 0:w_mid],
            edges[h_mid:h, w_mid:w]
        ]
        
        edge_densities = []
        for quad in quadrants:
            if quad.size > 0:
                density = np.sum(quad > 0) / quad.size
                edge_densities.append(density)
        
        if len(edge_densities) > 0:
            # Watermark memiliki distribusi edge yang relatif merata
            density_std = np.std(edge_densities)
            density_mean = np.mean(edge_densities)
            distribution_score = min(1.0, density_mean * 15) * (1 - min(1.0, density_std * 10))
        else:
            distribution_score = 0
        
        # Check 2: Texture analysis untuk repetitive pattern
        # Gunakan LBP (Local Binary Pattern) untuk deteksi texture
        lbp_radius = 2
        lbp_points = 8
        
        # Simple LBP implementation
        texture_score = 0
        if h > 10 and w > 10:
            # Sampling beberapa region untuk texture analysis
            sample_regions = [
                enhanced[h//4:3*h//4, w//4:3*w//4],  # Center region
                enhanced[h//6:h//3, w//3:2*w//3],    # Upper region
                enhanced[2*h//3:5*h//6, w//3:2*w//3] # Lower region
            ]
            
            texture_scores = []
            for region in sample_regions:
                if region.size > 100:
                    # Hitung variance dalam region (indicator texture complexity)
                    variance = np.var(region)
                    # Normalize variance score (watermark memiliki variance sedang)
                    normalized_var = min(1.0, variance / 800)  # Empirical threshold
                    texture_scores.append(normalized_var)
            
            if texture_scores:
                texture_score = np.mean(texture_scores)
        
        # Check 3: Frequency domain analysis
        # Watermark memiliki komponen frekuensi tertentu
        frequency_score = 0
        try:
            # DFT untuk analisis frekuensi
            f_transform = np.fft.fft2(enhanced)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Analisis distribusi energi di frekuensi menengah
            center_y, center_x = h//2, w//2
            
            # Ring sampling untuk mid-frequency analysis
            y, x = np.ogrid[:h, :w]
            mask_inner = ((x - center_x)**2 + (y - center_y)**2) > (min(h,w)//8)**2
            mask_outer = ((x - center_x)**2 + (y - center_y)**2) < (min(h,w)//3)**2
            ring_mask = mask_inner & mask_outer
            
            if np.sum(ring_mask) > 0:
                mid_freq_energy = np.mean(magnitude_spectrum[ring_mask])
                total_energy = np.mean(magnitude_spectrum)
                
                if total_energy > 0:
                    frequency_ratio = mid_freq_energy / total_energy
                    frequency_score = min(1.0, frequency_ratio * 2)  # Normalized
        except:
            frequency_score = 0
        
        # Kombinasi weighted scores
        final_score = (distribution_score * 0.4 + 
                      texture_score * 0.4 + 
                      frequency_score * 0.2)
        
        # Return score dengan threshold minimum
        return final_score if final_score >= 0.15 else 0
        
    except Exception as e:
        print(f"      Watermark detection error: {str(e)}")
        return 0
