"""
Screen Capture untuk Video Meeting
Capture lawan bicara dari screen video meeting
"""

import cv2
import numpy as np
import pyautogui
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime
from PIL import Image, ImageTk
import threading
import time

class VideoMeetingCapture:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Meeting Capture")
        self.root.geometry("400x300")
        
        # Variables
        self.capturing = False
        self.capture_area = None
        self.preview_active = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup user interface"""
        # Title
        title = tk.Label(self.root, text="Video Meeting Capture", font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Text(self.root, height=8, width=50)
        instructions.pack(pady=10)
        instructions.insert('1.0', """Cara Penggunaan:

1. Buka video meeting (Zoom/Teams/Meet/dll)
2. Klik 'Select Area' untuk pilih area video lawan bicara
3. Drag untuk select area yang ingin di-capture
4. Klik 'Start Preview' untuk preview real-time
5. Klik 'Capture' untuk ambil foto sesuai panduan KTP

Tips:
- Pastikan area yang dipilih mencakup wajah dan area KTP
- Preview akan menampilkan overlay panduan
- Hasil akan disimpan dengan timestamp""")
        instructions.config(state='disabled')
        
        # Buttons frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        # Select area button
        self.select_btn = tk.Button(btn_frame, text="Select Area", 
                                   command=self.select_capture_area,
                                   bg='#4CAF50', fg='white', width=12)
        self.select_btn.grid(row=0, column=0, padx=5)
        
        # Preview button
        self.preview_btn = tk.Button(btn_frame, text="Start Preview", 
                                    command=self.toggle_preview,
                                    bg='#2196F3', fg='white', width=12)
        self.preview_btn.grid(row=0, column=1, padx=5)
        
        # Capture button
        self.capture_btn = tk.Button(btn_frame, text="Capture", 
                                    command=self.capture_with_guides,
                                    bg='#FF9800', fg='white', width=12)
        self.capture_btn.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg='green')
        self.status_label.pack(pady=5)
        
        # Create static folder
        os.makedirs('static', exist_ok=True)
    
    def select_capture_area(self):
        """Select area untuk capture menggunakan mouse"""
        self.root.withdraw()  # Hide main window
        
        messagebox.showinfo("Select Area", 
                           "Klik dan drag untuk select area video lawan bicara.\n" +
                           "Pastikan area mencakup wajah dan tempat KTP akan ditunjukkan.")
        
        # Screenshot untuk selection
        screenshot = pyautogui.screenshot()
        screenshot_array = np.array(screenshot)
        
        # Create selection window
        self.create_selection_window(screenshot_array)
    
    def create_selection_window(self, screenshot):
        """Create window untuk area selection"""
        self.selection_window = tk.Toplevel()
        self.selection_window.title("Select Capture Area")
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.configure(bg='black')
        
        # Convert screenshot untuk tkinter
        screenshot_pil = Image.fromarray(screenshot)
        screenshot_tk = ImageTk.PhotoImage(screenshot_pil)
        
        # Canvas untuk drawing selection
        self.canvas = tk.Canvas(self.selection_window, 
                               width=screenshot.shape[1], 
                               height=screenshot.shape[0])
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)
        self.canvas.image = screenshot_tk  # Keep reference
        
        # Selection variables
        self.start_x = self.start_y = 0
        self.current_rect = None
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.end_selection)
        
        # Instructions
        instruction_label = tk.Label(self.selection_window, 
                                    text="Drag untuk select area. ESC untuk cancel.",
                                    fg='yellow', bg='black', font=('Arial', 12, 'bold'))
        instruction_label.place(x=10, y=10)
        
        # Bind ESC key
        self.selection_window.bind('<Escape>', lambda e: self.cancel_selection())
        self.selection_window.focus_set()
    
    def start_selection(self, event):
        """Start area selection"""
        self.start_x = event.x
        self.start_y = event.y
        
    def update_selection(self, event):
        """Update selection rectangle"""
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=2
        )
    
    def end_selection(self, event):
        """End area selection"""
        end_x, end_y = event.x, event.y
        
        # Calculate capture area
        self.capture_area = {
            'x': min(self.start_x, end_x),
            'y': min(self.start_y, end_y),
            'width': abs(end_x - self.start_x),
            'height': abs(end_y - self.start_y)
        }
        
        self.selection_window.destroy()
        self.root.deiconify()  # Show main window
        
        self.status_label.config(text=f"Area selected: {self.capture_area['width']}x{self.capture_area['height']}")
        
    def cancel_selection(self):
        """Cancel area selection"""
        self.selection_window.destroy()
        self.root.deiconify()
        self.status_label.config(text="Selection cancelled")
    
    def toggle_preview(self):
        """Toggle preview window"""
        if not self.capture_area:
            messagebox.showerror("Error", "Pilih area capture terlebih dahulu!")
            return
            
        if not self.preview_active:
            self.start_preview()
        else:
            self.stop_preview()
    
    def start_preview(self):
        """Start preview window dengan overlay"""
        self.preview_active = True
        self.preview_btn.config(text="Stop Preview")
        
        # Create preview window
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Preview dengan Panduan")
        self.preview_window.protocol("WM_DELETE_WINDOW", self.stop_preview)
        
        # Canvas untuk preview
        self.preview_canvas = tk.Canvas(self.preview_window, 
                                       width=self.capture_area['width'], 
                                       height=self.capture_area['height'])
        self.preview_canvas.pack()
        
        # Start preview thread
        self.preview_thread = threading.Thread(target=self.preview_loop, daemon=True)
        self.preview_thread.start()
    
    def preview_loop(self):
        """Loop untuk preview real-time"""
        while self.preview_active:
            try:
                # Capture area
                screenshot = pyautogui.screenshot(region=(
                    self.capture_area['x'], self.capture_area['y'],
                    self.capture_area['width'], self.capture_area['height']
                ))
                
                # Convert to numpy array
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Add guides overlay (same as app.py)
                frame_with_guides = self.add_guides_overlay(frame)
                
                # Convert back for tkinter
                frame_rgb = cv2.cvtColor(frame_with_guides, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                
                # Update preview canvas
                if self.preview_active:
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=frame_tk)
                    self.preview_canvas.image = frame_tk  # Keep reference
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                print(f"Preview error: {e}")
                break
    
    def add_guides_overlay(self, frame):
        """Add guides overlay seperti di app.py"""
        h, w = frame.shape[:2]
        
        # Calculate proportional coordinates (same as app.py)
        base_w, base_h = 640, 480
        scale_x = w / base_w
        scale_y = h / base_h
        
        padding_h = int(186 * scale_x)
        padding_v = int(31 * scale_y)
        gap = int(25 * scale_y)
        
        content_width = w - (padding_h * 2)
        content_height = h - (padding_v * 2)
        
        # Face area
        face_w = int(207 * scale_x)
        face_h = int(223 * scale_y)
        face_x = padding_h + (content_width - face_w) // 2
        face_y = padding_v
        
        # KTP area
        ktp_x = padding_h
        ktp_y = face_y + face_h + gap
        ktp_w = content_width
        ktp_h = content_height - face_h - gap
        
        # Create overlay dengan opacity 50%
        overlay = frame.copy()
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Face area (oval)
        face_center_x = face_x + face_w // 2
        face_center_y = face_y + face_h // 2
        face_radius_x = face_w // 2
        face_radius_y = face_h // 2
        
        cv2.ellipse(mask, (face_center_x, face_center_y), (face_radius_x, face_radius_y), 
                   0, 0, 360, 255, -1)
        
        # KTP area (rectangle)
        cv2.rectangle(mask, (ktp_x, ktp_y), (ktp_x + ktp_w, ktp_y + ktp_h), 255, -1)
        
        # Apply overlay
        overlay[mask == 0] = [0, 0, 0]
        alpha = 0.5
        beta = 1.0 - alpha
        frame = cv2.addWeighted(frame, beta, overlay, alpha, 0)
        
        # Draw guides
        cv2.ellipse(frame, (face_center_x, face_center_y), (face_radius_x, face_radius_y), 
                   0, 0, 360, (255, 255, 255), 2)
        cv2.rectangle(frame, (ktp_x, ktp_y), (ktp_x + ktp_w, ktp_y + ktp_h), 
                     (255, 255, 255), 2)
        
        # Store coordinates for capture
        self.face_coords = (face_x, face_y, face_w, face_h)
        self.ktp_coords = (ktp_x, ktp_y, ktp_w, ktp_h)
        
        return frame
    
    def stop_preview(self):
        """Stop preview"""
        self.preview_active = False
        self.preview_btn.config(text="Start Preview")
        
        if hasattr(self, 'preview_window'):
            self.preview_window.destroy()
    
    def capture_with_guides(self):
        """Capture dengan coordinates guides"""
        if not self.capture_area:
            messagebox.showerror("Error", "Pilih area capture terlebih dahulu!")
            return
            
        if not hasattr(self, 'face_coords') or not hasattr(self, 'ktp_coords'):
            messagebox.showerror("Error", "Jalankan preview terlebih dahulu untuk kalkulasi coordinates!")
            return
        
        try:
            # Capture current screen area
            screenshot = pyautogui.screenshot(region=(
                self.capture_area['x'], self.capture_area['y'],
                self.capture_area['width'], self.capture_area['height']
            ))
            
            # Convert to OpenCV format
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Get coordinates
            face_x, face_y, face_w, face_h = self.face_coords
            ktp_x, ktp_y, ktp_w, ktp_h = self.ktp_coords
            
            h, w = frame.shape[:2]
            
            # Ensure coordinates are within bounds
            face_x = max(0, min(face_x, w))
            face_y = max(0, min(face_y, h))
            face_x2 = min(w, face_x + face_w)
            face_y2 = min(h, face_y + face_h)
            
            ktp_x = max(0, min(ktp_x, w))
            ktp_y = max(0, min(ktp_y, h))
            ktp_x2 = min(w, ktp_x + ktp_w)
            ktp_y2 = min(h, ktp_y + ktp_h)
            
            # Crop images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_files = []
            
            if face_x2 > face_x and face_y2 > face_y:
                face_crop = frame[face_y:face_y2, face_x:face_x2]
                if face_crop.size > 0:
                    face_resized = cv2.resize(face_crop, (300, 300))
                    face_path = f'static/meeting_face_{timestamp}.jpg'
                    cv2.imwrite(face_path, face_resized)
                    saved_files.append(f"Face: {face_path}")
            
            if ktp_x2 > ktp_x and ktp_y2 > ktp_y:
                ktp_crop = frame[ktp_y:ktp_y2, ktp_x:ktp_x2]
                if ktp_crop.size > 0:
                    ktp_resized = cv2.resize(ktp_crop, (480, 300))
                    ktp_path = f'static/meeting_ktp_{timestamp}.jpg'
                    cv2.imwrite(ktp_path, ktp_resized)
                    saved_files.append(f"KTP: {ktp_path}")
            
            # Save full screenshot for reference
            full_path = f'static/meeting_full_{timestamp}.jpg'
            cv2.imwrite(full_path, frame)
            saved_files.append(f"Full: {full_path}")
            
            # Show result
            if saved_files:
                result_msg = f"✅ Capture berhasil!\n\n" + "\n".join(saved_files)
                result_msg += f"\n\nTimestamp: {timestamp}"
                messagebox.showinfo("Capture Success", result_msg)
                self.status_label.config(text=f"Captured: {timestamp}")
            else:
                messagebox.showwarning("Warning", "Tidak ada area yang berhasil di-capture!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saat capture: {str(e)}")
    
    def run(self):
        """Start application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("=== Video Meeting Capture ===")
    print("Capture lawan bicara dari screen video meeting")
    print("Dengan panduan KTP yang sama seperti aplikasi utama")
    print()
    
    app = VideoMeetingCapture()
    app.run()
