# Whisper-Fast-GUI

**English** | [简体中文](README.zh-CN.md)

A lightweight desktop application for transcribing audio and video with
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper). The interface is
built entirely with Python's standard `tkinter` library, keeping the project
small, portable, and easy to run on Windows.

## Features

- **Lightweight and portable** — the interface and application logic are kept
  in a compact Python codebase without a heavyweight GUI framework.
- **Local model storage** — downloaded models are stored in `./models/` next to
  the application instead of filling the system drive.
- **GPU acceleration** — powered by CTranslate2 and faster-whisper, with NVIDIA
  CUDA acceleration support.
- **Drag and drop** — drop audio or video files onto the window to add them to
  the processing queue.
- **Saved preferences** — remembers the selected model, compute type, output
  formats, and hardware device.
- **Multiple export formats** — generate SRT, VTT, and TXT files in one run.
- **Task controls** — stop an active transcription while allowing hardware
  resources to be released cleanly.
- **Built-in cleanup** — remove downloaded models and caches, or uninstall the
  application from the GUI or with `Uninstall.bat`.
- **Silent Windows launcher** — start the application with
  `Start-WhisperGUI.vbs` without keeping a Command Prompt window open.

## Requirements

- Windows
- Python 3.9 or later
- An NVIDIA GPU is optional; CPU transcription is supported

## Installation

Clone or download this repository, open a terminal in the project directory,
and install the dependencies:

```bash
pip install -r requirements.txt
```

### NVIDIA CUDA runtime

If faster-whisper reports that `cublas64_12.dll` is missing or exits with error
`0xc0000142`, install the required CUDA runtime packages:

```bash
pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12
```

The application includes runtime library discovery, so you do not need to edit
environment variables manually.

## Usage

### Launch without a console window (recommended on Windows)

Double-click `Start-WhisperGUI.vbs`.

### Launch from a terminal

```bash
python WhisperGUI.py
```

Then choose a Whisper model and hardware device, select one or more output
formats, add your media files, and start transcription. Models are downloaded
automatically on first use.

## Model storage and cleanup

Models are saved under:

```text
./models/
```

Keeping models inside the project directory makes the application easy to move
between folders or external drives.

To reclaim disk space, use the **🗑️ 卸载与清理 (Uninstall & Cleanup)** action in
the top-right corner of the application and select either model/cache cleanup
or a complete uninstall. You can also double-click `Uninstall.bat` while the
application is closed.

## Contributing

Pull requests and issue reports are welcome. Potential areas for improvement
include:

- Multilingual transcription and translation workflows
- Vocal separation
- GUI and interaction refinements

## License

No license file is currently included. Unless a license is added, normal
copyright restrictions apply to the source code.
