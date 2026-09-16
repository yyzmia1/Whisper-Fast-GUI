# Whisper-Fast-GUI

**English** | [简体中文](README.zh-CN.md)

Turn audio and video into subtitle files on your own Windows PC.

Whisper-Fast-GUI gives [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper)
a simple desktop interface. Add your files, choose a model, and export subtitles
without uploading your media to an online transcription service.

## Why use it?

- **Private by design** — transcription runs locally on your computer.
- **Easy batch processing** — select multiple files or drag them into the app.
- **Useful output formats** — export SRT, VTT, and plain-text transcripts.
- **CPU and NVIDIA GPU support** — use whatever hardware is available.
- **China-friendly downloads** — switch between the official Hugging Face Hub
  and the `hf-mirror.com` mirror.
- **Portable storage** — models and settings stay inside the application folder,
  making cleanup and moving the app straightforward.

Supported media shortcuts include MP4, AVI, MKV, MOV, MP3, WAV, FLAC, and M4A.

## Before you start

You need:

- Windows
- Python 3.9 or later
- Internet access the first time each model is downloaded
- An NVIDIA GPU only if you want GPU acceleration; CPU mode also works

> [!NOTE]
> This project is currently distributed as source code, not as a prebuilt
> `.exe` installer. Python must be installed before the app can run.
> The current application interface is in Simplified Chinese; this guide adds
> English explanations for the controls.

## Quick start

### 1. Download the project

[Download the latest ZIP](https://github.com/yyzmiao/Whisper-Fast-GUI/archive/refs/heads/main.zip),
then extract it to a folder with enough free space for the Whisper models.

### 2. Install Python

Install Python 3.9 or later. On the Windows installer, enable
**Add python.exe to PATH**.

### 3. Install the required packages

Open a terminal inside the extracted project folder and run:

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the app

Double-click:

```text
Start-WhisperGUI.vbs
```

This opens the app without leaving a Command Prompt window on screen. You can
also start it from a terminal with `python WhisperGUI.py`.

## How to create subtitles

1. Choose a model and select **GPU** or **CPU**.
2. Select the output formats you need: **SRT**, **VTT**, and/or **TXT**.
3. Choose a model download source. Use the China mirror if the official source
   is slow or unavailable on your network.
4. Click **1. Select media files**, or drag files into the window.
5. Click **2. Start transcription**.

The generated subtitle files are saved next to each original media file.

## Which model should I choose?

| Model | Best for | Trade-off |
| --- | --- | --- |
| `tiny` / `base` | Quick drafts and older computers | Fastest, but less accurate |
| `small` | A practical starting point for CPU users | Good balance of speed and accuracy |
| `medium` | Better accuracy on capable hardware | Slower and uses more memory |
| `large-v3` | Best available accuracy in this app | A capable NVIDIA GPU is recommended |

The first run with a model takes longer because its files must be downloaded.
Later runs reuse the copy stored in `./models/`.

## Download sources and the `HF_TOKEN` warning

- **Hugging Face official** is the default. Public models can be downloaded
  without an account. A warning about unauthenticated requests is not an error;
  it only means anonymous requests have lower rate limits.
- **China mirror (`hf-mirror.com`)** can help when the official source is slow
  or unreachable. The app does not send your Hugging Face token to this
  third-party mirror.

Authentication is optional. To get higher rate limits from the official source,
run this once and follow the prompt:

```powershell
hf auth login
```

You can also provide an `HF_TOKEN` environment variable before launching the
app. Tokens are never saved in `.whisper_gui_config.json`.

## Common questions

### The first transcription seems stuck

The selected model may still be downloading. Larger models take longer and need
more disk space. Watch the app's log area and wait for **Model loaded** before
assuming the task has failed.

### I see `cublas64_12.dll is not found` or error `0xc0000142`

Install the optional NVIDIA CUDA runtime packages:

```powershell
python -m pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Restart the app afterward. If you do not need GPU acceleration, select CPU mode.

### Where are the downloaded models?

They are stored in the project's `models` folder, not in the default Hugging
Face cache on the system drive.

### How do I free the model storage?

Use **🗑️ Uninstall & Cleanup** in the top-right corner of the app. You can also
run `Uninstall.bat` while the app is closed.

### Is my media uploaded anywhere?

No. Audio and video transcription happens locally. Network access is used to
download model files only.

## For developers

```powershell
git clone https://github.com/yyzmiao/Whisper-Fast-GUI.git
cd Whisper-Fast-GUI
python -m pip install -r requirements.txt
python WhisperGUI.py
```

Issues and pull requests are welcome.

## License

No license file is currently included. Unless a license is added, normal
copyright restrictions apply to the source code.
