"""
Screen Overlay Application
Overlay transparan yang bisa ditampilkan di atas aplikasi video call
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class TransparentOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.width = 640
        self.height = 480
        self.scale_factor = 1.0
        self.setup_window()
        self.setup_guides()
        self.dragging = False
        self.resizing = False
        self.drag_x = 0
        self.drag_y = 0
        
    def setup_window(self):
        """Setup window transparan"""
        self.root.title("KTP Face Guide Overlay")
        
        # Window settings
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-transparentcolor', 'black')  # Transparent black
        self.root.configure(bg='black')
        
        # Set size (bisa disesuaikan)
        self.root.geometry(f"{self.width}x{self.height}+100+100")  # +x+y for position
        
        # Make window draggable and resizable
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.on_drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Key bindings untuk adjustment
        self.root.bind('<KeyPress-Escape>', lambda e: self.root.quit())
        self.root.bind('<KeyPress-h>', lambda e: self.toggle_visibility())
        self.root.bind('<KeyPress-plus>', lambda e: self.resize_overlay(1.1))  # Zoom in
        self.root.bind('<KeyPress-minus>', lambda e: self.resize_overlay(0.9))  # Zoom out
        self.root.bind('<KeyPress-equal>', lambda e: self.resize_overlay(1.1))  # + key
        self.root.bind('<KeyPress-underscore>', lambda e: self.resize_overlay(0.9))  # - key
        self.root.bind('<KeyPress-r>', lambda e: self.reset_size())  # Reset size
        self.root.bind('<KeyPress-f>', lambda e: self.fit_to_screen())  # Fit to screen
        self.root.focus_set()
        
    def setup_guides(self):
        """Setup visual guides"""
        # Main canvas
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
        self.canvas.delete("all")  # Clear canvas
        
        # Create semi-transparent overlay
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill='gray',
            stipple='gray50',  # 50% opacity pattern
            outline=''
        )
        
        # Calculate proportional coordinates based on current size
        base_w, base_h = 640, 480
        scale_x = self.width / base_w
        scale_y = self.height / base_h
        
        # Proportional coordinates
        padding_h = int(186 * scale_x)
        padding_v = int(31 * scale_y)
        gap = int(25 * scale_y)
        
        content_width = self.width - (padding_h * 2)
        content_height = self.height - (padding_v * 2)
        
        # Face guide (oval) - coordinates yang proporsional
        face_w = int(207 * scale_x)
        face_h = int(223 * scale_y)
        face_x = padding_h + (content_width - face_w) // 2
        face_y = padding_v
        
        # KTP guide (rectangle)
        ktp_x = padding_h
        ktp_y = face_y + face_h + gap
        ktp_w = content_width
        ktp_h = content_height - face_h - gap
        
        # Clear face area (make transparent)
        self.canvas.create_oval(
            face_x, face_y, face_x + face_w, face_y + face_h,
            fill='black',  # Transparent
            outline='white',
            width=2
        )
        
        # Clear KTP area (make transparent)
        self.canvas.create_rectangle(
            ktp_x, ktp_y, ktp_x + ktp_w, ktp_y + ktp_h,
            fill='black',  # Transparent
            outline='white',
            width=2
        )
        
        # Instructions text - adjust font size based on scale
        font_size = max(8, int(10 * min(scale_x, scale_y)))
        self.canvas.create_text(
            self.width//2, 15,
            text=f"ESC:Close | H:Hide | +/-:Resize | R:Reset | F:Fit | Size:{self.width}x{self.height}",
            fill='yellow',
            font=('Arial', font_size, 'bold')
        )
        
        # Face label
        face_font_size = max(10, int(16 * min(scale_x, scale_y)))
        self.canvas.create_text(
            face_x + face_w//2, face_y + face_h//2,
            text="WAJAH",
            fill='white',
            font=('Arial', face_font_size, 'bold')
        )
        
        # KTP label
        ktp_font_size = max(10, int(16 * min(scale_x, scale_y)))
        self.canvas.create_text(
            ktp_x + ktp_w//2, ktp_y + ktp_h//2,
            text="KTP",
            fill='white',
            font=('Arial', ktp_font_size, 'bold')
        )
    
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
        
        # Limit ukuran minimum dan maksimum
        min_size = 200
        max_size = 1920
        
        if min_size <= new_width <= max_size and min_size <= new_height <= max_size:
            self.width = new_width
            self.height = new_height
            
            # Update window geometry
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            self.root.geometry(f"{self.width}x{self.height}+{current_x}+{current_y}")
            
            # Update canvas size
            self.canvas.config(width=self.width, height=self.height)
            
            # Redraw guides
            self.redraw_guides()
    
    def reset_size(self):
        """Reset ke ukuran default"""
        self.width = 640
        self.height = 480
        self.scale_factor = 1.0
        
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        self.root.geometry(f"{self.width}x{self.height}+{current_x}+{current_y}")
        
        self.canvas.config(width=self.width, height=self.height)
        self.redraw_guides()
    
    def fit_to_screen(self):
        """Fit overlay ke ukuran layar saat ini"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Gunakan 80% dari ukuran layar
        self.width = int(screen_width * 0.8)
        self.height = int(screen_height * 0.8)
        
        # Center di layar
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        self.canvas.config(width=self.width, height=self.height)
        self.redraw_guides()
    
    def run(self):
        """Start overlay application"""
        print("=== Screen Overlay untuk Video Call (Enhanced) ===")
        print("Controls:")
        print("  Drag: Move overlay position")
        print("  + (Plus): Zoom in / Make bigger")
        print("  - (Minus): Zoom out / Make smaller") 
        print("  R: Reset to default size (640x480)")
        print("  F: Fit to screen size")
        print("  H: Hide/show overlay")
        print("  ESC: Close application")
        print()
        print("Usage:")
        print("1. Buka aplikasi video call")
        print("2. Drag overlay ke posisi video preview")
        print("3. Gunakan +/- untuk adjust ukuran sesuai video")
        print("4. Position lingkaran untuk wajah dan kotak untuk KTP")
        print()
        
        self.root.mainloop()

class ControlPanel:
    def __init__(self, overlay):
        self.overlay = overlay
        self.control_window = tk.Toplevel()
        self.setup_control_panel()
        
    def setup_control_panel(self):
        """Setup control panel window"""
        self.control_window.title("Overlay Control")
        self.control_window.geometry("300x200+50+50")
        self.control_window.attributes('-topmost', True)
        
        # Buttons
        ttk.Button(
            self.control_window,
            text="Toggle Overlay (H)",
            command=self.overlay.toggle_visibility
        ).pack(pady=5)
        
        ttk.Button(
            self.control_window,
            text="Zoom In (+)",
            command=lambda: self.overlay.resize_overlay(1.2)
        ).pack(pady=2)
        
        ttk.Button(
            self.control_window,
            text="Zoom Out (-)",
            command=lambda: self.overlay.resize_overlay(0.8)
        ).pack(pady=2)
        
        ttk.Button(
            self.control_window,
            text="Reset Size (R)",
            command=self.overlay.reset_size
        ).pack(pady=2)
        
        ttk.Button(
            self.control_window,
            text="Fit to Screen (F)",
            command=self.overlay.fit_to_screen
        ).pack(pady=2)
        
        ttk.Button(
            self.control_window,
            text="Close All",
            command=self.close_all
        ).pack(pady=10)
        
        # Instructions
        instructions = tk.Text(self.control_window, height=10, width=40)
        instructions.pack(pady=10)
        instructions.insert('1.0', """Enhanced Overlay Controls:

KEYBOARD SHORTCUTS:
• + / = : Zoom in (make bigger)
• - / _ : Zoom out (make smaller)  
• R : Reset to default size
• F : Fit to screen
• H : Hide/show overlay
• ESC : Close application
• Drag : Move position

USAGE STEPS:
1. Position overlay over video call preview
2. Use +/- to match video size exactly
3. Align guides with your face and KTP
4. Hide overlay (H) when not needed

TIP: Use Control Panel buttons if keyboard 
shortcuts don't work in your video app.""")
        instructions.config(state='disabled')
        
    def close_all(self):
        """Close all windows"""
        self.control_window.destroy()
        self.overlay.root.quit()

if __name__ == "__main__":
    # Create overlay
    overlay = TransparentOverlay()
    
    # Create control panel in separate thread
    def create_control():
        time.sleep(0.5)  # Wait for overlay to initialize
        control = ControlPanel(overlay)
    
    control_thread = threading.Thread(target=create_control)
    control_thread.daemon = True
    control_thread.start()
    
    # Run overlay
    overlay.run()
