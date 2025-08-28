"""
Template Analysis Utility
Tool untuk menganalisis dan mengoptimalkan template KTP detection
"""
import cv2
import numpy as np
import os

def analyze_template_characteristics(template_path):
    """
    Analyze characteristics of a KTP template
    """
    if not os.path.exists(template_path):
        return None
    
    template = cv2.imread(template_path)
    if template is None:
        return None
    
    # Basic properties
    h, w, c = template.shape
    
    # Color analysis
    gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Brightness analysis
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    
    # Blue header analysis (for KTP detection)
    hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    header_region = hsv[:int(h*0.3), :]  # Top 30%
    
    # Blue color range
    lower_blue = np.array([90, 40, 40])
    upper_blue = np.array([140, 255, 255])
    blue_mask = cv2.inRange(header_region, lower_blue, upper_blue)
    blue_ratio = np.sum(blue_mask > 0) / (header_region.shape[0] * header_region.shape[1])
    
    # Edge analysis
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / (w * h)
    
    # Contrast analysis
    contrast = np.std(gray)
    
    return {
        'path': template_path,
        'filename': os.path.basename(template_path),
        'dimensions': (w, h),
        'aspect_ratio': w/h,
        'mean_brightness': mean_brightness,
        'brightness_std': std_brightness,
        'blue_header_ratio': blue_ratio,
        'edge_density': edge_density,
        'contrast': contrast,
        'suitable_for_detection': blue_ratio > 0.1 and contrast > 20
    }

def analyze_all_templates():
    """
    Analyze all templates in assets folder
    """
    assets_dir = r"C:\Users\rdest\OneDrive\Documents\photo-detection\assets"
    
    template_files = [
        'template_ktp.png',
        'template_ktp_improved.png', 
        'template_brightness_-30.png',
        'template_brightness_-15.png',
        'template_brightness_+0.png',
        'template_brightness_+15.png',
        'template_brightness_+30.png'
    ]
    
    results = []
    
    print("🔍 Analyzing KTP Templates...")
    print("=" * 80)
    
    for filename in template_files:
        template_path = os.path.join(assets_dir, filename)
        analysis = analyze_template_characteristics(template_path)
        
        if analysis:
            results.append(analysis)
            
            print(f"📄 {analysis['filename']}")
            print(f"   📐 Dimensions: {analysis['dimensions'][0]}x{analysis['dimensions'][1]} (aspect: {analysis['aspect_ratio']:.2f})")
            print(f"   💡 Brightness: {analysis['mean_brightness']:.1f} ± {analysis['brightness_std']:.1f}")
            print(f"   🔵 Blue header: {analysis['blue_header_ratio']:.3f}")
            print(f"   📊 Edge density: {analysis['edge_density']:.3f}")
            print(f"   🎯 Contrast: {analysis['contrast']:.1f}")
            print(f"   ✅ Good for detection: {analysis['suitable_for_detection']}")
            print("-" * 40)
        else:
            print(f"❌ Failed to analyze: {filename}")
    
    # Find best templates
    suitable_templates = [t for t in results if t['suitable_for_detection']]
    
    if suitable_templates:
        # Sort by blue header ratio (most important for KTP detection)
        best_template = max(suitable_templates, key=lambda x: x['blue_header_ratio'])
        
        print(f"\n🏆 Best template for detection: {best_template['filename']}")
        print(f"   Blue header ratio: {best_template['blue_header_ratio']:.3f}")
        print(f"   Contrast: {best_template['contrast']:.1f}")
        
        # Find templates for different lighting conditions
        bright_templates = [t for t in suitable_templates if t['mean_brightness'] > 140]
        dark_templates = [t for t in suitable_templates if t['mean_brightness'] < 100]
        normal_templates = [t for t in suitable_templates if 100 <= t['mean_brightness'] <= 140]
        
        print(f"\n📋 Templates by lighting condition:")
        print(f"   🌞 Bright conditions: {len(bright_templates)} templates")
        print(f"   🌙 Dark conditions: {len(dark_templates)} templates") 
        print(f"   ☀️ Normal conditions: {len(normal_templates)} templates")
        
        return {
            'all_templates': results,
            'suitable_templates': suitable_templates,
            'best_template': best_template,
            'bright_templates': bright_templates,
            'dark_templates': dark_templates,
            'normal_templates': normal_templates
        }
    
    return {'all_templates': results}

def recommend_detection_strategy():
    """
    Recommend detection strategy based on available templates
    """
    analysis = analyze_all_templates()
    
    print(f"\n🎯 DETECTION STRATEGY RECOMMENDATIONS:")
    print("=" * 50)
    
    suitable = analysis.get('suitable_templates', [])
    
    if len(suitable) > 1:
        print("✅ Multi-template approach recommended:")
        print("   1. Use brightness-specific templates based on frame analysis")
        print("   2. Try multiple templates and pick best confidence")
        print("   3. Adaptive template selection based on lighting")
        
        if 'bright_templates' in analysis and analysis['bright_templates']:
            bright = analysis['bright_templates'][0]
            print(f"   🌞 For bright frames: {bright['filename']}")
            
        if 'normal_templates' in analysis and analysis['normal_templates']:
            normal = analysis['normal_templates'][0] 
            print(f"   ☀️ For normal frames: {normal['filename']}")
            
        if 'dark_templates' in analysis and analysis['dark_templates']:
            dark = analysis['dark_templates'][0]
            print(f"   🌙 For dark frames: {dark['filename']}")
            
    elif len(suitable) == 1:
        template = suitable[0]
        print(f"✅ Single template approach: {template['filename']}")
        print("   Good baseline template, but consider adding brightness variations")
        
    else:
        print("❌ No suitable templates found!")
        print("   Consider improving template quality or blue header detection")
    
    # Performance recommendations
    print(f"\n⚡ PERFORMANCE RECOMMENDATIONS:")
    if len(suitable) <= 3:
        print("   ✅ Current template count is good for real-time performance")
    else:
        print("   ⚠️ Many templates may slow down detection")
        print("   Consider pre-filtering templates based on frame characteristics")

if __name__ == "__main__":
    recommend_detection_strategy()
