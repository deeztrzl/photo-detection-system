"""
Enhanced KTP Template System
Template management dengan adaptive selection berdasarkan lighting conditions
"""
import cv2
import numpy as np
import os
from typing import Dict, List, Tuple, Optional

class KTPTemplateManager:
    """
    Advanced template management system for KTP detection
    """
    
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.templates: Dict[str, Dict] = {}
        self.primary_template = None
        self.load_all_templates()
        
    def load_all_templates(self):
        """Load and analyze all available templates"""
        template_files = {
            'primary': 'template_ktp.png',  # High blue header ratio
            'improved': 'template_ktp_improved.png',
            'bright': 'template_brightness_+30.png',
            'normal_bright': 'template_brightness_+15.png', 
            'normal': 'template_brightness_+0.png',
            'normal_dark': 'template_brightness_-15.png',
            'dark': 'template_brightness_-30.png'
        }
        
        for template_type, filename in template_files.items():
            template_path = os.path.join(self.assets_dir, filename)
            template_info = self._load_template(template_path, template_type)
            
            if template_info:
                self.templates[template_type] = template_info
                if template_type == 'primary':
                    self.primary_template = template_info
        
        print(f"✅ Loaded {len(self.templates)} templates")
        
    def _load_template(self, template_path: str, template_type: str) -> Optional[Dict]:
        """Load single template with analysis"""
        if not os.path.exists(template_path):
            return None
            
        try:
            template = cv2.imread(template_path)
            if template is None:
                return None
                
            # Standardize size
            h, w = template.shape[:2]
            if w > 300:  # Resize large templates for performance
                new_w = 300
                new_h = int(h * (new_w / w))
                template = cv2.resize(template, (new_w, new_h))
            
            # Analyze template characteristics
            gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Blue header analysis
            hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
            header_region = hsv[:int(hsv.shape[0]*0.3), :]
            lower_blue = np.array([90, 40, 40])
            upper_blue = np.array([140, 255, 255])
            blue_mask = cv2.inRange(header_region, lower_blue, upper_blue)
            blue_ratio = np.sum(blue_mask > 0) / (header_region.shape[0] * header_region.shape[1])
            
            return {
                'template': template,
                'gray': gray,
                'path': template_path,
                'type': template_type,
                'brightness': brightness,
                'contrast': contrast,
                'blue_ratio': blue_ratio,
                'size': template.shape[:2],
                'quality_score': blue_ratio * 0.7 + (contrast / 100) * 0.3
            }
            
        except Exception as e:
            print(f"⚠️ Error loading template {template_path}: {e}")
            return None
    
    def get_best_template_for_frame(self, frame: np.ndarray) -> Dict:
        """
        Select best template based on frame characteristics
        """
        if not self.templates:
            return None
            
        # Analyze frame brightness
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_brightness = np.mean(gray_frame)
        
        # Template selection strategy
        if frame_brightness > 150:
            # Very bright frame - try bright templates first
            priority_order = ['primary', 'bright', 'normal_bright', 'normal', 'improved']
        elif frame_brightness > 120:
            # Normal-bright frame 
            priority_order = ['primary', 'normal_bright', 'normal', 'bright', 'improved']
        elif frame_brightness > 90:
            # Normal frame
            priority_order = ['primary', 'normal', 'normal_dark', 'normal_bright', 'improved']
        elif frame_brightness > 60:
            # Dark frame
            priority_order = ['primary', 'normal_dark', 'dark', 'normal', 'improved']
        else:
            # Very dark frame
            priority_order = ['primary', 'dark', 'normal_dark', 'normal', 'improved']
        
        # Return first available template from priority order
        for template_type in priority_order:
            if template_type in self.templates:
                template_info = self.templates[template_type].copy()
                template_info['selection_reason'] = f"frame_brightness_{frame_brightness:.1f}"
                return template_info
        
        # Fallback to primary if available
        if self.primary_template:
            fallback = self.primary_template.copy()
            fallback['selection_reason'] = "fallback_primary"
            return fallback
            
        return None
    
    def get_all_suitable_templates(self) -> List[Dict]:
        """
        Get all templates suitable for detection (with good blue header)
        """
        suitable = []
        for template_info in self.templates.values():
            if template_info['blue_ratio'] > 0.1:  # Has reasonable blue header
                suitable.append(template_info)
        
        # Sort by quality score
        suitable.sort(key=lambda x: x['quality_score'], reverse=True)
        return suitable
    
    def get_primary_template(self) -> Optional[Dict]:
        """Get the primary template (highest quality)"""
        return self.primary_template
    
    def get_template_info(self) -> Dict:
        """Get summary of all loaded templates"""
        info = {
            'total_templates': len(self.templates),
            'templates_by_type': {},
            'quality_summary': {}
        }
        
        for template_type, template_info in self.templates.items():
            info['templates_by_type'][template_type] = {
                'brightness': template_info['brightness'],
                'blue_ratio': template_info['blue_ratio'],
                'quality_score': template_info['quality_score']
            }
        
        suitable_templates = self.get_all_suitable_templates()
        info['quality_summary'] = {
            'suitable_templates': len(suitable_templates),
            'best_template': suitable_templates[0]['type'] if suitable_templates else None,
            'avg_quality': np.mean([t['quality_score'] for t in suitable_templates]) if suitable_templates else 0
        }
        
        return info

# Global template manager instance
template_manager = None

def initialize_template_manager(assets_dir: str) -> KTPTemplateManager:
    """Initialize global template manager"""
    global template_manager
    template_manager = KTPTemplateManager(assets_dir)
    return template_manager

def get_template_manager() -> Optional[KTPTemplateManager]:
    """Get global template manager instance"""
    return template_manager

def get_adaptive_template(frame: np.ndarray) -> Optional[Dict]:
    """
    Get best template for current frame
    Convenience function for backward compatibility
    """
    if template_manager:
        return template_manager.get_best_template_for_frame(frame)
    return None

def get_primary_template() -> Optional[np.ndarray]:
    """
    Get primary template for backward compatibility
    """
    if template_manager and template_manager.primary_template:
        return template_manager.primary_template['template']
    return None
