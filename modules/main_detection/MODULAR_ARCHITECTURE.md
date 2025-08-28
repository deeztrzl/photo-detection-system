# Photo Detection System - Modular Architecture

## 📁 Project Structure

```
modules/main_detection/
├── app.py                          # Main application entry point (28 lines)
├── core/                           # Core modules
│   ├── __init__.py
│   ├── config.py                   # Configuration and global settings (85 lines)
│   └── video_stream.py             # Video streaming with overlay (122 lines)
├── detection/                      # Detection algorithms
│   ├── __init__.py
│   ├── face_detector.py            # Face detection using MediaPipe (50 lines)
│   ├── ktp_detector.py             # KTP detection using 2-layer system (130 lines)
│   └── main_detector.py            # Main detection coordinator (40 lines)
├── routes/                         # Flask routes
│   ├── __init__.py
│   ├── main_routes.py              # Main application routes (52 lines)
│   └── capture_routes.py           # Capture and file management (150 lines)
├── static/                         # Static files
└── templates/                      # HTML templates
```

## 🎯 Modular Benefits

### Before (Monolithic)
- **Single file:** `app.py` with **681 lines**
- Hard to maintain and debug
- Difficult to test individual components
- Code reusability limited

### After (Modular)
- **Main app:** `app.py` with only **28 lines**
- **8 focused modules** with clear responsibilities
- Easy to maintain, test, and extend
- Better code organization and reusability

## 📋 Module Responsibilities

### 1. **app.py** (Main Entry Point)
- Application factory pattern
- Route initialization
- Startup configuration
- **28 lines** - clean and minimal

### 2. **core/config.py** (Configuration)
- Global variables and settings
- Template loading
- Camera initialization
- Coordinate calculations
- **85 lines**

### 3. **core/video_stream.py** (Video Streaming)
- Real-time video stream with overlays
- Manual guide rendering
- Status bar information
- **122 lines**

### 4. **detection/face_detector.py** (Face Detection)
- MediaPipe face detection
- KTP face detection from captured KTP
- **50 lines**

### 5. **detection/ktp_detector.py** (KTP Detection)
- 2-layer KTP detection system
- Color and shape analysis (Layer 1)
- Template matching verification (Layer 2)
- **130 lines**

### 6. **detection/main_detector.py** (Detection Coordinator)
- Combines face and KTP detection
- Main detection entry point
- **40 lines**

### 7. **routes/main_routes.py** (Main Routes)
- Index, video feed, mode toggle
- Detection status endpoint
- **52 lines**

### 8. **routes/capture_routes.py** (Capture Routes)
- Photo capture functionality
- File management and downloads
- **150 lines**

## 🚀 Advantages of New Structure

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Scalability**: Easy to add new features without affecting others
4. **Reusability**: Modules can be reused in other projects
5. **Debugging**: Easier to locate and fix issues
6. **Team Development**: Multiple developers can work on different modules

## 🔧 Key Features Preserved

- ✅ 2-layer KTP detection system (HSV + Template matching)
- ✅ Real-time video streaming with overlays
- ✅ Auto and manual capture modes
- ✅ File management and downloads
- ✅ Template matching with 78% threshold
- ✅ All original functionality intact

## 📈 Performance Impact

- **No performance loss** - same algorithms and processing
- **Better memory management** through focused imports
- **Faster development** due to modular structure
- **Easier debugging** with clear module boundaries

## 🛠️ Usage

The application works exactly the same as before:

```bash
cd modules/main_detection
python app.py
```

Access at: http://localhost:8080

All original features and APIs remain unchanged!
