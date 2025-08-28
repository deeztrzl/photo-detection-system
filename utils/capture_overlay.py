"""
Screen Overlay dengan Capture Function
Overlay transparan + kemampuan capture seperti aplikasi utama
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import threading
import time
import os
from datetime import datetime
import numpy as np

class CaptureOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.width = 640
        self.height = 480
        self.setup_window()
        self.setup_guides()
        
        # Camera setup dengan error handling
        self.cap = None
        self.camera_available = False
        self.init_camera()
        
        # Drag variables
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        
        # Create static folder
        os.makedirs('static', exist_ok=True)
    
    def init_camera(self):
        """Initialize camera dengan error handling"""
        try:
            # Coba berbagai camera index
            for camera_id in [0, 1, 2]:
                print(f"Mencoba camera {camera_id}...")
                test_cap = cv2.VideoCapture(camera_id)
                if test_cap.isOpened():
                    ret, frame = test_cap.read()
                    if ret:
                        self.cap = test_cap
                        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        self.camera_available = True
                        print(f"✅ Camera {camera_id} berhasil diinisialisasi")
                        return
                    else:
                        test_cap.release()
                else:
                    test_cap.release()
            
            print("❌ Tidak ada camera yang tersedia")
            self.camera_available = False
            
        except Exception as e:
            print(f"❌ Error inisialisasi camera: {e}")
            self.camera_available = False
        
    def setup_window(self):
        """Setup window transparan"""
        self.root.title("KTP Face Guide Overlay + Capture")
        
        # Window settings
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        self.root.configure(bg='black')
        
        self.root.geometry(f"{self.width}x{self.height}+100+100")
        
        # Mouse bindings
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.on_drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        self.root.bind('<Button-3>', self.show_context_menu)  # Right click
        
        # Key bindings
        self.root.bind('<KeyPress-Escape>', lambda e: self.root.quit())
        self.root.bind('<KeyPress-h>', lambda e: self.toggle_visibility())
        self.root.bind('<KeyPress-plus>', lambda e: self.resize_overlay(1.1))
        self.root.bind('<KeyPress-minus>', lambda e: self.resize_overlay(0.9))
        self.root.bind('<KeyPress-equal>', lambda e: self.resize_overlay(1.1))
        self.root.bind('<KeyPress-underscore>', lambda e: self.resize_overlay(0.9))
        self.root.bind('<KeyPress-r>', lambda e: self.reset_size())
        self.root.bind('<KeyPress-f>', lambda e: self.fit_to_screen())
        self.root.bind('<KeyPress-c>', lambda e: self.capture_manual())  # Capture key
        self.root.bind('<KeyPress-space>', lambda e: self.capture_manual())  # Space for capture
        self.root.focus_set()
        
    def setup_guides(self):
        """Setup visual guides"""
        self.canvas = tk.Canvas(
            self.root, 
            bg='black',
            highlightthickness=0,
            width=self.width,
            height=self.height
        )
        self.canvas.pack(fill='both', expand=True)
        self.redraw_guides()
    
    def redraw_guides(self):
        """Redraw guides dengan ukuran yang disesuaikan"""
        self.canvas.delete("all")
        
        # Semi-transparent overlay
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill='gray',
            stipple='gray50',
            outline=''
        )
        
        # Calculate proportional coordinates
        base_w, base_h = 640, 480
        scale_x = self.width / base_w
        scale_y = self.height / base_h
        
        # Proportional coordinates (same as app.py)
        padding_h = int(186 * scale_x)
        padding_v = int(31 * scale_y)
        gap = int(25 * scale_y)
        
        content_width = self.width - (padding_h * 2)
        content_height = self.height - (padding_v * 2)
        
        # Face area
        face_w = int(207 * scale_x)
        face_h = int(223 * scale_y)
        face_x = padding_h + (content_width - face_w) // 2
        face_y = padding_v
        
        # Store coordinates for capture
        self.face_coords = (face_x, face_y, face_w, face_h)
        
        # KTP area
        ktp_x = padding_h
        ktp_y = face_y + face_h + gap
        ktp_w = content_width
        ktp_h = content_height - face_h - gap
        
        # Store coordinates for capture
        self.ktp_coords = (ktp_x, ktp_y, ktp_w, ktp_h)
        
        # Clear areas (transparent)
        self.canvas.create_oval(
            face_x, face_y, face_x + face_w, face_y + face_h,
            fill='black',
            outline='white',
            width=2
        )
        
        self.canvas.create_rectangle(
            ktp_x, ktp_y, ktp_x + ktp_w, ktp_y + ktp_h,
            fill='black',
            outline='white',
            width=2
        )
        
        # Instructions
        font_size = max(8, int(10 * min(scale_x, scale_y)))
        self.canvas.create_text(
            self.width//2, 15,
            text=f"SPACE/C:Capture | H:Hide | +/-:Resize | Right-click:Menu | Size:{self.width}x{self.height}",
            fill='yellow',
            font=('Arial', font_size, 'bold')
        )
        
        # Labels
        face_font_size = max(10, int(16 * min(scale_x, scale_y)))
        self.canvas.create_text(
            face_x + face_w//2, face_y + face_h//2,
            text="WAJAH",
            fill='white',
            font=('Arial', face_font_size, 'bold')
        )
        
        ktp_font_size = max(10, int(16 * min(scale_x, scale_y)))
        self.canvas.create_text(
            ktp_x + ktp_w//2, ktp_y + ktp_h//2,
            text="KTP",
            fill='white',
            font=('Arial', ktp_font_size, 'bold')
        )
    
    def show_context_menu(self, event):
        """Show context menu on right click"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="📸 Capture (Space/C)", command=self.capture_manual)
        context_menu.add_separator()
        context_menu.add_command(label="🔍 Zoom In (+)", command=lambda: self.resize_overlay(1.2))
        context_menu.add_command(label="🔍 Zoom Out (-)", command=lambda: self.resize_overlay(0.8))
        context_menu.add_command(label="↺ Reset Size (R)", command=self.reset_size)
        context_menu.add_command(label="⛶ Fit Screen (F)", command=self.fit_to_screen)
        context_menu.add_separator()
        context_menu.add_command(label="👁 Hide/Show (H)", command=self.toggle_visibility)
        context_menu.add_command(label="📁 Open Folder", command=self.open_results_folder)
        context_menu.add_separator()
        context_menu.add_command(label="❌ Close (Esc)", command=self.root.quit)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def capture_manual(self):
        """Capture menggunakan koordinat overlay"""
        # Check camera availability
        if not self.camera_available or self.cap is None:
            messagebox.showerror("Error", "Kamera tidak tersedia!\n\nPossible solutions:\n1. Pastikan kamera tidak digunakan aplikasi lain\n2. Tutup aplikasi video call yang menggunakan kamera\n3. Restart aplikasi ini\n4. Check kamera di Device Manager")
            return
            
        if hasattr(self, 'capturing') and self.capturing:
            return
            
        self.capturing = True
        
        try:
            # Test camera access
            if not self.cap.isOpened():
                # Try to reinitialize
                self.init_camera()
                if not self.camera_available:
                    raise Exception("Camera tidak dapat diakses setelah reinisialisasi")
            
            # Get frame from camera
            success, frame = self.cap.read()
            if not success:
                raise Exception("Tidak dapat membaca frame dari kamera")
            
            # Check if frame is valid
            if frame is None or frame.size == 0:
                raise Exception("Frame kamera kosong")
            
            # Get camera resolution
            cam_h, cam_w = frame.shape[:2]
            print(f"📷 Camera resolution: {cam_w}x{cam_h}")
            
            # Calculate scale from overlay to camera resolution
            scale_x = cam_w / self.width
            scale_y = cam_h / self.height
            print(f"📐 Scale factors: x={scale_x:.2f}, y={scale_y:.2f}")
            
            # Convert overlay coordinates to camera coordinates
            face_x, face_y, face_w, face_h = self.face_coords
            ktp_x, ktp_y, ktp_w, ktp_h = self.ktp_coords
            
            # Scale coordinates to camera resolution
            cam_face_x = int(face_x * scale_x)
            cam_face_y = int(face_y * scale_y)
            cam_face_w = int(face_w * scale_x)
            cam_face_h = int(face_h * scale_y)
            
            cam_ktp_x = int(ktp_x * scale_x)
            cam_ktp_y = int(ktp_y * scale_y)
            cam_ktp_w = int(ktp_w * scale_x)
            cam_ktp_h = int(ktp_h * scale_y)
            
            # Ensure coordinates are within bounds
            cam_face_x = max(0, min(cam_face_x, cam_w))
            cam_face_y = max(0, min(cam_face_y, cam_h))
            cam_face_x2 = min(cam_w, cam_face_x + cam_face_w)
            cam_face_y2 = min(cam_h, cam_face_y + cam_face_h)
            
            cam_ktp_x = max(0, min(cam_ktp_x, cam_w))
            cam_ktp_y = max(0, min(cam_ktp_y, cam_h))
            cam_ktp_x2 = min(cam_w, cam_ktp_x + cam_ktp_w)
            cam_ktp_y2 = min(cam_h, cam_ktp_y + cam_ktp_h)
            
            print(f"📍 Face coords: ({cam_face_x},{cam_face_y}) to ({cam_face_x2},{cam_face_y2})")
            print(f"📍 KTP coords: ({cam_ktp_x},{cam_ktp_y}) to ({cam_ktp_x2},{cam_ktp_y2})")
            
            # Crop images
            face_img = None
            ktp_img = None
            
            if cam_face_x2 > cam_face_x and cam_face_y2 > cam_face_y:
                face_crop = frame[cam_face_y:cam_face_y2, cam_face_x:cam_face_x2]
                if face_crop.size > 0:
                    face_img = cv2.resize(face_crop, (300, 300))
                    print("✅ Face crop berhasil")
            
            if cam_ktp_x2 > cam_ktp_x and cam_ktp_y2 > cam_ktp_y:
                ktp_crop = frame[cam_ktp_y:cam_ktp_y2, cam_ktp_x:cam_ktp_x2]
                if ktp_crop.size > 0:
                    ktp_img = cv2.resize(ktp_crop, (480, 300))
                    print("✅ KTP crop berhasil")
            
            # Save images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_files = []
            
            if face_img is not None:
                face_path = f'static/face_capture_{timestamp}.jpg'
                cv2.imwrite(face_path, face_img)
                saved_files.append(f"Face: {face_path}")
                print(f"💾 Saved: {face_path}")
            
            if ktp_img is not None:
                ktp_path = f'static/ktp_capture_{timestamp}.jpg'
                cv2.imwrite(ktp_path, ktp_img)
                saved_files.append(f"KTP: {ktp_path}")
                print(f"💾 Saved: {ktp_path}")
            
            # Show result
            if saved_files:
                result_msg = f"✅ Capture berhasil!\n\n" + "\n".join(saved_files)
                result_msg += f"\n\nTimestamp: {timestamp}"
                result_msg += f"\nCamera: {cam_w}x{cam_h}, Overlay: {self.width}x{self.height}"
                messagebox.showinfo("Capture Success", result_msg)
                print("🎉 Capture berhasil!")
            else:
                messagebox.showwarning("Warning", "Tidak ada area yang berhasil di-capture!\nPastikan overlay align dengan objek di kamera.")
                
        except Exception as e:
            error_msg = f"Error saat capture: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(f"❌ {error_msg}")
        finally:
            self.capturing = False
    
    def open_results_folder(self):
        """Buka folder hasil capture"""
        try:
            os.startfile('static')
        except:
            messagebox.showinfo("Folder", "Hasil capture tersimpan di folder: static/")
    
    def start_drag(self, event):
        """Start dragging window"""
        self.dragging = True
        self.drag_x = event.x
        self.drag_y = event.y
    
    def on_drag(self, event):
        """Handle window dragging"""
        if self.dragging:
            x = self.root.winfo_x() + (event.x - self.drag_x)
            y = self.root.winfo_y() + (event.y - self.drag_y)
            self.root.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """Stop dragging window"""
        self.dragging = False
    
    def toggle_visibility(self):
        """Toggle window visibility"""
        if self.root.state() == 'normal':
            self.root.withdraw()
        else:
            self.root.deiconify()
    
    def resize_overlay(self, factor):
        """Resize overlay dengan factor tertentu"""
        new_width = int(self.width * factor)
        new_height = int(self.height * factor)
        
        min_size = 200
        max_size = 1920
        
        if min_size <= new_width <= max_size and min_size <= new_height <= max_size:
            self.width = new_width
            self.height = new_height
            
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            self.root.geometry(f"{self.width}x{self.height}+{current_x}+{current_y}")
            
            self.canvas.config(width=self.width, height=self.height)
            self.redraw_guides()
    
    def reset_size(self):
        """Reset ke ukuran default"""
        self.width = 640
        self.height = 480
        
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        self.root.geometry(f"{self.width}x{self.height}+{current_x}+{current_y}")
        
        self.canvas.config(width=self.width, height=self.height)
        self.redraw_guides()
    
    def fit_to_screen(self):
        """Fit overlay ke ukuran layar saat ini"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.width = int(screen_width * 0.8)
        self.height = int(screen_height * 0.8)
        
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        self.canvas.config(width=self.width, height=self.height)
        self.redraw_guides()
    
    def run(self):
        """Start overlay application"""
        print("=== KTP Face Overlay + Capture ===")
        
        if self.camera_available:
            print("✅ Camera berhasil diinisialisasi")
        else:
            print("❌ Camera tidak tersedia - Capture akan disabled")
            print("   Pastikan:")
            print("   1. Kamera tidak digunakan aplikasi lain")
            print("   2. Tutup video call yang menggunakan kamera")
            print("   3. Check Device Manager untuk status kamera")
        
        print()
        print("Controls:")
        print("  SPACE/C: Capture photo based on overlay position")
        print("  Right-click: Context menu")
        print("  Drag: Move overlay position")
        print("  +/-: Zoom in/out")
        print("  R: Reset size")
        print("  F: Fit to screen")
        print("  H: Hide/show")
        print("  ESC: Close")
        print()
        print("Usage:")
        print("1. Position overlay over video call preview")
        print("2. Adjust size with +/- to match video")
        print("3. Align guides over face and KTP areas")
        print("4. Press SPACE or C to capture!")
        print("5. Check static/ folder for results")
        print()
        
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
            print("🧹 Camera released")

if __name__ == "__main__":
    app = CaptureOverlay()
    app.run()
