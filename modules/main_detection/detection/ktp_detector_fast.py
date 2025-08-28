"""
Fast KTP Detection Module - Optimized for Performance
Simple and efficient KTP detection without heavy feature matching
"""
import cv2
import numpy as np
import sys
import os

# Add path to access config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import get_ktp_template

def lightweight_template_match(candidate_crop, ktp_template):
    """
    Lightweight template matching to distinguish KTP from other blue cards
    """
    try:
        # Resize both to same size for comparison
        target_height = 150
        target_width = int(target_height * 1.6)  # KTP aspect ratio
        
        # Resize candidate
        candidate_resized = cv2.resize(candidate_crop, (target_width, target_height))
        
        # Resize template
        template_resized = cv2.resize(ktp_template, (target_width, target_height))
        
        # Convert to grayscale
        candidate_gray = cv2.cvtColor(candidate_resized, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template_resized, cv2.COLOR_BGR2GRAY)
        
        # Focus on header area (top 30% where "REPUBLIK INDONESIA" text is)
        header_height = int(target_height * 0.3)
        candidate_header = candidate_gray[:header_height, :]
        template_header = template_gray[:header_height, :]
        
        # Simple correlation matching on header
        result = cv2.matchTemplate(candidate_header, template_header, cv2.TM_CCOEFF_NORMED)
        max_val = np.max(result)
        
        # Edge pattern matching for text structure
        candidate_edges = cv2.Canny(candidate_header, 50, 150)
        template_edges = cv2.Canny(template_header, 50, 150)
        
        # Compare edge patterns
        edge_similarity = cv2.matchTemplate(candidate_edges, template_edges, cv2.TM_CCOEFF_NORMED)
        edge_score = np.max(edge_similarity)
        
        # Combine scores
        final_template_score = (max_val * 0.7 + edge_score * 0.3)
        
        print(f"      📋 Template details: correlation={max_val:.3f}, edge={edge_score:.3f}, final={final_template_score:.3f}")
        
        return final_template_score
        
    except Exception as e:
        print(f"      ❌ Template matching error: {str(e)}")
        return 0.3  # Low but not zero score on error

def detect_ktp_candidates_by_color_and_shape(frame):
    """
    Fast Layer 1: Lightweight candidate detection
    """
    candidates = []
    h, w, _ = frame.shape
    
    print(f"🔍 Scanning frame {w}x{h} for KTP candidates...")
    
    # Resize for speed if frame is too large
    scale = 0.5 if min(h, w) > 640 else 1.0
    if scale < 1.0:
        work_frame = cv2.resize(frame, None, fx=scale, fy=scale)
        print(f"   Resized to {work_frame.shape[1]}x{work_frame.shape[0]} (scale={scale})")
    else:
        work_frame = frame
    
    # Convert to HSV
    hsv = cv2.cvtColor(work_frame, cv2.COLOR_BGR2HSV)
    
    # Indonesian KTP blue header - EXTREMELY STRICT range
    lower_blue = np.array([105, 80, 80])  # Very specific blue only
    upper_blue = np.array([120, 255, 255])  # Much narrower range
    
    # Create blue mask
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # AGGRESSIVE noise reduction to filter most false positives
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # Larger kernel
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_ERODE, kernel)  # Extra erosion
    
    # Find contours
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"   Found {len(contours)} blue contours")
    
    # Early exit if no significant blue areas
    if len(contours) == 0:
        print("   ❌ No blue contours found")
        return candidates
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        
        # EXTREMELY STRICT minimum area to avoid ANY small blue objects
        min_area = 5000 * (scale ** 2)  # Increased from 2000 to 5000
        
        print(f"   Contour {i+1}: area={area:.0f} (min={min_area:.0f})")
        
        if area > min_area:
            x, y, w2, h2 = cv2.boundingRect(contour)
            
            # Scale back coordinates if needed
            if scale < 1.0:
                x = int(x / scale)
                y = int(y / scale)
                w2 = int(w2 / scale)
                h2 = int(h2 / scale)
            
            aspect_ratio = w2 / h2 if h2 > 0 else 0
            
            print(f"      Size: {w2}x{h2}, aspect={aspect_ratio:.2f}")
            
            # EXTREMELY STRICT KTP aspect ratio range
            if 1.55 <= aspect_ratio <= 1.85:  # Very narrow KTP-specific range
                # Quick blue ratio check on original frame
                roi = frame[y:y+h2, x:x+w2]
                roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                roi_blue_mask = cv2.inRange(roi_hsv, lower_blue, upper_blue)
                blue_ratio = cv2.countNonZero(roi_blue_mask) / (w2 * h2)
                
                print(f"      Blue ratio: {blue_ratio:.3f}")
                
                # EXTREMELY STRICT blue ratio threshold
                if blue_ratio >= 0.6:  # Very high threshold - 60% blue content required
                    print(f"🔍 Fast KTP Candidate: {w2}x{h2}, aspect={aspect_ratio:.2f}, blue_ratio={blue_ratio:.2f}")
                    candidates.append((x, y, w2, h2, area, blue_ratio))
                else:
                    print(f"   ❌ Rejected: blue_ratio {blue_ratio:.3f} < 0.6")
            else:
                print(f"   ❌ Rejected: aspect ratio {aspect_ratio:.2f} not in [1.55, 1.85]")
        else:
            print(f"   ❌ Rejected: area {area:.0f} < {min_area:.0f}")
    
    # Limit to 2 best candidates to avoid lag
    if len(candidates) > 2:
        candidates = sorted(candidates, key=lambda x: x[5], reverse=True)[:2]
        print(f"   📊 Limited to top 2 candidates")
    
    if len(candidates) == 0:
        print("   ❌ NO VALID KTP CANDIDATES FOUND")
    else:
        print(f"   ✅ {len(candidates)} candidate(s) passed initial screening")
    
    return candidates

def verify_ktp_candidate_fast(frame, candidate_region):
    """
    Fast KTP verification WITH lightweight template matching
    """
    try:
        x, y, w, h, area, blue_ratio = candidate_region
        
        # Basic validation
        if w < 50 or h < 30:
            return 0.0, None
        
        frame_height, frame_width = frame.shape[:2]
        if x + w > frame_width or y + h > frame_height:
            return 0.0, None
        
        candidate_crop = frame[y:y+h, x:x+w]
        if candidate_crop.size == 0:
            return 0.0, None
        
        print(f"   🔍 Fast verification: {w}x{h} at ({x},{y}) with blue_ratio={blue_ratio:.2f}")
        
        # Load KTP template for comparison
        ktp_template = get_ktp_template()
        if ktp_template is None:
            print("   ⚠️ Warning: No KTP template loaded, proceeding without template matching")
            template_score = 0.5  # Neutral score
        else:
            # Lightweight template matching
            template_score = lightweight_template_match(candidate_crop, ktp_template)
            print(f"   📋 Template Match Score: {template_score:.3f}")
        
        # 1. Blue header score (most important for KTP) - Stricter
        header_score = 1.0 if blue_ratio >= 0.5 else (0.6 if blue_ratio >= 0.4 else 0.2)
        
        # 2. Template matching score (NEW - prevents false positives from other blue cards)
        # This will distinguish KTP from credit cards, SIM cards, etc.
        
        # 3. Enhanced texture score with anti-digital validation
        gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (w * h)
        
        # Digital/PDF detection: Check for uniform patterns (pixelation artifacts)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_peaks = np.sum(hist > np.max(hist) * 0.1)  # Count significant peaks
        digital_penalty = 0.3 if hist_peaks < 10 else 0.0  # Penalize too few gray levels
        
        texture_score = max(0.0, min(edge_density * 8, 1.0) - digital_penalty)
        
        # 4. Size score (stricter)
        size_score = 1.0 if (80 <= w <= 400 and 50 <= h <= 250) else 0.4
        
        # 5. Aspect ratio score (stricter)
        aspect_ratio = w / h
        aspect_score = 1.0 if (1.5 <= aspect_ratio <= 1.9) else 0.4
        
        print(f"   📊 Fast Scores - Header: {header_score:.2f}, Template: {template_score:.2f}, Texture: {texture_score:.2f}, Size: {size_score:.2f}, Aspect: {aspect_score:.2f}")
        
        # NEW 5-component scoring with template matching
        final_score = (header_score * 0.3 + template_score * 0.3 + texture_score * 0.2 + size_score * 0.1 + aspect_score * 0.1)
        
        # Higher threshold to block fake KTPs AND other blue cards
        if final_score >= 0.65 and template_score >= 0.4:  # Must pass both overall AND template threshold
            print(f"   ✅ FAST KTP VERIFICATION PASSED! Score: {final_score:.3f} (Template: {template_score:.3f})")
            return final_score, {
                'confidence': final_score,
                'header_score': header_score,
                'template_score': template_score,
                'texture_score': texture_score,
                'size_score': size_score,
                'region': candidate_region
            }
        else:
            print(f"   ❌ FAST KTP VERIFICATION FAILED! Score: {final_score:.3f}, Template: {template_score:.3f} (need both ≥0.65 and template ≥0.4)")
            return 0.0, None
            
    except Exception as e:
        print(f"   ❌ Error in fast verification: {str(e)}")
        return 0.0, None

def detect_ktp_in_frame(frame):
    """
    Main KTP detection function - FAST VERSION
    """
    print("🔍 Layer 1: Detecting KTP candidates by color and shape...")
    candidates = detect_ktp_candidates_by_color_and_shape(frame)
    
    if not candidates:
        print("❌ No KTP candidates found in Layer 1")
        return False, 0.0, None
    
    print(f"   Found {len(candidates)} KTP candidate(s)")
    print("🎯 Layer 2: Verifying candidates with fast matching...")
    
    best_confidence = 0.0
    best_result = None
    
    for i, candidate in enumerate(candidates):
        print(f"   Testing candidate {i+1}/{len(candidates)}")
        confidence, result = verify_ktp_candidate_fast(frame, candidate)
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_result = result
    
    if best_confidence > 0:
        print(f"✅ KTP VERIFIED! Final confidence: {best_confidence:.3f}")
        return True, best_confidence, best_result
    else:
        print("❌ No candidates passed template verification")
        return False, 0.0, None
