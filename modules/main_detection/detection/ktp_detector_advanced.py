"""
Advanced KTP Detection Module - Feature Matching Approach
Using ORB + SIFT + Homography for robust authentic KTP detection
"""
import cv2
import numpy as np
import sys
import os

# Add path to access config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import get_ktp_template

# Initialize feature detectors with fewer features for better performance
orb = cv2.ORB_create(nfeatures=500)  # Reduced from 1000
try:
    sift = cv2.SIFT_create(nfeatures=200)  # Reduced from 500
    SIFT_AVAILABLE = True
except AttributeError:
    print("⚠️ SIFT not available, using ORB only")
    SIFT_AVAILABLE = False

# FLANN matcher for SIFT
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

# BFMatcher for ORB
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Global template features (will be loaded lazily)
TEMPLATE_KP_ORB = None
TEMPLATE_DES_ORB = None
TEMPLATE_KP_SIFT = None
TEMPLATE_DES_SIFT = None
TEMPLATE_LOADED = False

def extract_template_features():
    """Extract features from KTP template once at startup"""
    global TEMPLATE_KP_ORB, TEMPLATE_DES_ORB, TEMPLATE_KP_SIFT, TEMPLATE_DES_SIFT, TEMPLATE_LOADED
    
    if TEMPLATE_LOADED:
        return TEMPLATE_KP_ORB, TEMPLATE_DES_ORB, TEMPLATE_KP_SIFT, TEMPLATE_DES_SIFT
    
    # Find project root and construct absolute path
    current_file = os.path.abspath(__file__)
    project_root = current_file
    for _ in range(4):  # Go up 4 levels from detection/ktp_detector_advanced.py
        project_root = os.path.dirname(project_root)
    
    # Direct absolute path to KTP template
    template_path = os.path.join(project_root, "assets", "ktp muka.png")
    
    print(f"🔍 Looking for template at: {template_path}")
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found at: {template_path}")
        return None, None, None, None
    
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ Could not read template from: {template_path}")
        return None, None, None, None
    
    print(f"✅ Template loaded successfully from: {template_path}")
    
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Extract ORB features
    kp_orb, des_orb = orb.detectAndCompute(gray_template, None)
    
    # Extract SIFT features if available
    kp_sift, des_sift = None, None
    if SIFT_AVAILABLE:
        kp_sift, des_sift = sift.detectAndCompute(gray_template, None)
    
    # Cache results
    TEMPLATE_KP_ORB = kp_orb
    TEMPLATE_DES_ORB = des_orb
    TEMPLATE_KP_SIFT = kp_sift
    TEMPLATE_DES_SIFT = des_sift
    TEMPLATE_LOADED = True
    
    print(f"✅ Template features extracted: ORB={len(kp_orb) if kp_orb else 0}, SIFT={len(kp_sift) if kp_sift else 0}")
    
    return kp_orb, des_orb, kp_sift, des_sift

def detect_ktp_candidates_by_color_and_shape(frame):
    """
    Layer 1: Enhanced candidate detection with stricter filtering
    """
    candidates = []
    h, w, _ = frame.shape
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # More precise blue range for Indonesian KTP
    lower_blue = np.array([100, 60, 60])   # Stricter blue
    upper_blue = np.array([125, 255, 255])
    
    # Create mask for blue regions
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Size filtering - KTP should be reasonable size
        if 0.005 * h * w < area < 0.5 * h * w:  # 0.5% to 50% of frame
            x, y, w2, h2 = cv2.boundingRect(contour)
            aspect_ratio = w2 / h2 if h2 > 0 else 0
            
            # KTP aspect ratio is approximately 1.6:1 (85.6mm x 53.98mm)
            if 1.35 <= aspect_ratio <= 1.85:  # Stricter aspect ratio
                # Calculate blue ratio in the region
                roi_mask = blue_mask[y:y+h2, x:x+w2]
                blue_pixels = cv2.countNonZero(roi_mask)
                total_pixels = w2 * h2
                blue_ratio = blue_pixels / total_pixels if total_pixels > 0 else 0
                
                # Higher blue ratio requirement
                if blue_ratio >= 0.35:  # At least 35% blue
                    print(f"🔍 Enhanced KTP Candidate: {w2}x{h2}, aspect={aspect_ratio:.2f}, blue_ratio={blue_ratio:.2f}")
                    candidates.append((x, y, w2, h2, area, blue_ratio))
    
    # Sort by blue ratio (higher is better for authentic KTP)
    candidates.sort(key=lambda x: x[5], reverse=True)
    return candidates

def advanced_feature_matching(candidate_crop):
    """
    Advanced feature matching using ORB + SIFT + Homography
    """
    # Load template features if not already loaded
    kp_orb_template, des_orb_template, kp_sift_template, des_sift_template = extract_template_features()
    
    if des_orb_template is None:
        print(f"   ❌ Template features not available")
        return 0.0
    
    gray_candidate = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
    
    # Extract features from candidate
    kp_orb, des_orb = orb.detectAndCompute(gray_candidate, None)
    
    if des_orb is None or len(des_orb) < 10:
        print("   ❌ Insufficient ORB features in candidate")
        return 0.0
    
    # ORB matching
    orb_matches = bf.match(des_orb_template, des_orb)
    orb_matches = sorted(orb_matches, key=lambda x: x.distance)
    
    good_orb_matches = [m for m in orb_matches if m.distance < 50]  # Stricter threshold
    orb_score = len(good_orb_matches) / max(len(kp_orb_template), len(kp_orb)) if len(kp_orb) > 0 else 0
    
    print(f"   🔍 ORB matches: {len(good_orb_matches)}/{len(orb_matches)}, score: {orb_score:.3f}")
    
    # SIFT matching (if available)
    sift_score = 0.0
    if SIFT_AVAILABLE and des_sift_template is not None:
        kp_sift, des_sift = sift.detectAndCompute(gray_candidate, None)
        
        if des_sift is not None and len(des_sift) >= 4:
            matches = flann.knnMatch(des_sift_template, des_sift, k=2)
            
            # Apply Lowe's ratio test
            good_sift_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.7 * n.distance:  # Stricter ratio
                        good_sift_matches.append(m)
            
            sift_score = len(good_sift_matches) / max(len(kp_sift_template), len(kp_sift)) if len(kp_sift) > 0 else 0
            print(f"   🔍 SIFT matches: {len(good_sift_matches)}, score: {sift_score:.3f}")
            
            # Homography validation for geometric consistency
            if len(good_sift_matches) >= 8:  # Need minimum matches for homography
                src_pts = np.float32([kp_sift_template[m.queryIdx].pt for m in good_sift_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_sift[m.trainIdx].pt for m in good_sift_matches]).reshape(-1, 1, 2)
                
                try:
                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    if M is not None:
                        inliers = np.sum(mask)
                        homography_score = inliers / len(good_sift_matches)
                        print(f"   🔍 Homography inliers: {inliers}/{len(good_sift_matches)}, score: {homography_score:.3f}")
                        sift_score *= homography_score  # Multiply by geometric consistency
                except:
                    print("   ❌ Homography calculation failed")
    
    # Combined feature score
    if SIFT_AVAILABLE:
        combined_score = (orb_score * 0.4) + (sift_score * 0.6)  # SIFT weighted higher
    else:
        combined_score = orb_score
    
    return combined_score

def texture_analysis(candidate_crop):
    """
    Analyze texture patterns specific to authentic KTP
    """
    gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
    
    # Local Binary Pattern (LBP) for texture
    def lbp(image, radius=1, n_points=8):
        h, w = image.shape
        lbp_img = np.zeros((h, w), dtype=np.uint8)
        
        for i in range(radius, h - radius):
            for j in range(radius, w - radius):
                center = image[i, j]
                code = 0
                for k in range(n_points):
                    angle = 2 * np.pi * k / n_points
                    x = int(i + radius * np.cos(angle))
                    y = int(j + radius * np.sin(angle))
                    if image[x, y] >= center:
                        code |= (1 << k)
                lbp_img[i, j] = code
        return lbp_img
    
    # Calculate LBP
    lbp_img = lbp(gray)
    
    # Calculate texture uniformity
    hist, _ = np.histogram(lbp_img.ravel(), bins=256, range=[0, 256])
    hist = hist.astype(float)
    hist /= (hist.sum() + 1e-7)  # Normalize
    
    # Calculate entropy (lower entropy = more uniform texture like authentic KTP)
    entropy = -np.sum(hist * np.log2(hist + 1e-7))
    
    # Authentic KTP should have moderate entropy (not too uniform, not too chaotic)
    if 4.0 <= entropy <= 6.5:
        texture_score = 1.0
    elif 3.5 <= entropy <= 7.0:
        texture_score = 0.7
    else:
        texture_score = 0.3
    
    print(f"   🔍 Texture entropy: {entropy:.2f}, score: {texture_score:.2f}")
    return texture_score

def verify_ktp_candidate_by_advanced_matching(frame, candidate_region):
    """
    OPTIMIZED KTP verification with reduced complexity for better performance
    """
    try:
        x, y, w, h, area, blue_ratio = candidate_region
        
        # Quick validation
        if x < 0 or y < 0 or w <= 0 or h <= 0 or w < 50 or h < 30:
            return 0.0, None
            
        frame_height, frame_width = frame.shape[:2]
        if x + w > frame_width or y + h > frame_height:
            return 0.0, None
        
        candidate_crop = frame[y:y+h, x:x+w]
        if candidate_crop.size == 0:
            return 0.0, None
        
        print(f"   🔍 Fast verification: {w}x{h} at ({x},{y}) with blue_ratio={blue_ratio:.2f}")
        
        # FAST MODE: Simplified scoring
        
        # 1. Quick feature check (ORB only, limited features)
        feature_score = 0.0
        kp_orb_template, des_orb_template, _, _ = extract_template_features()
        
        if des_orb_template is not None:
            gray_candidate = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
            kp_orb, des_orb = orb.detectAndCompute(gray_candidate, None)
            
            if des_orb is not None and len(des_orb) >= 3:  # Very low threshold
                try:
                    matches = bf.match(des_orb_template, des_orb)
                    if len(matches) > 3:
                        matches = sorted(matches, key=lambda x: x.distance)[:5]  # Top 5 only
                        good_matches = [m for m in matches if m.distance < 70]  # Very lenient
                        feature_score = min(len(good_matches) / 5, 1.0)  # Quick normalize
                except:
                    feature_score = 0.0
        
        # 2. Simple texture check (histogram entropy)
        gray = cv2.cvtColor(candidate_crop, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [16], [0, 256])  # Reduced bins for speed
        hist = hist.flatten() + 1e-7
        entropy = -np.sum(hist * np.log(hist))
        texture_score = min(entropy / 8.0, 1.0)  # Quick normalize
        
        # 3. Quick header check (just look for blue in top region)
        header_score = 1.0 if blue_ratio >= 0.4 else (0.5 if blue_ratio >= 0.25 else 0.0)
        
        # 4. Size check
        size_score = 1.0 if (60 <= w <= 500 and 40 <= h <= 300) else 0.5
        
        print(f"   📊 Fast Scores - Feature: {feature_score:.3f}, Texture: {texture_score:.2f}, Header: {header_score:.2f}, Size: {size_score:.2f}")
        
        # Simplified scoring (reduced weight on expensive feature matching)
        final_score = (feature_score * 0.3 + texture_score * 0.3 + header_score * 0.3 + size_score * 0.1)
        
        # More lenient threshold for better usability
        if final_score >= 0.2:  # Lower threshold
            print(f"   ✅ FAST KTP VERIFICATION PASSED! Score: {final_score:.3f}")
            return final_score, {
                'confidence': final_score,
                'feature_score': feature_score,
                'texture_score': texture_score,
                'header_score': header_score,
                'region': candidate_region
            }
        else:
            print(f"   ❌ FAST KTP VERIFICATION FAILED! Score: {final_score:.3f}")
            return 0.0, None
            
    except Exception as e:
        print(f"   ❌ Error in fast verification: {str(e)}")
        return 0.0, None
