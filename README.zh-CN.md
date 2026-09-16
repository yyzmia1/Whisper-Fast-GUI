# Whisper-Fast-GUI

[English](README.md) | **简体中文**

Whisper-Fast-GUI 是一个基于
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) 的轻量级音视频字幕提取桌面工具。图形界面完全使用 Python 内置的 `tkinter` 编写，项目小巧、便携，适合在 Windows 上使用。

## 主要特性

- **轻量便携**：不依赖大型 GUI 框架，界面与主要逻辑集中在简洁的 Python 代码中。
- **模型本地存储**：模型默认下载至程序同级的 `./models/`，避免占用系统盘的全局缓存空间。
- **下载源切换**：可在界面中切换 Hugging Face 官方源与 `hf-mirror.com` 国内镜像。
- **GPU 加速**：底层基于 CTranslate2 与 faster-whisper，支持 NVIDIA CUDA 加速。
- **文件拖拽**：可将音频或视频文件直接拖入窗口，自动加入处理队列。
- **配置记忆**：自动保存所选模型、计算精度、输出格式和硬件设备。
- **多格式导出**：支持一次生成 SRT、VTT 和 TXT 文件。
- **任务控制**：可中止正在执行的转录任务，并正常释放硬件资源。
- **一键清理**：可在界面内清理模型和缓存，也可通过 `Uninstall.bat` 完成清理或卸载。
- **静默启动**：通过 `Start-WhisperGUI.vbs` 启动时不会保留命令行窗口。

## 环境要求

- Windows
- Python 3.9 或更高版本
- NVIDIA 显卡为可选项，也支持使用 CPU 转录

## 安装

克隆或下载本仓库，在项目目录中打开终端并安装依赖：

```bash
pip install -r requirements.txt
```

### NVIDIA CUDA 运行库

如果 faster-whisper 提示缺少 `cublas64_12.dll`，或程序以 `0xc0000142` 错误退出，请安装所需的 CUDA 运行库：

```bash
pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12
```

程序已包含运行库路径查找逻辑，无需手动修改环境变量。

### 模型下载源与 `HF_TOKEN`

开始任务前，可在界面中选择模型下载源：

- **Hugging Face 官方源**为默认选项。公开模型无需登录也能下载；未认证请求的 Warning 只是提示匿名请求的速率额度较低，并非下载错误。
- **国内镜像（`hf-mirror.com`）**适合无法稳定直连 Hugging Face 的网络环境。为了安全，程序不会把 Hugging Face Token 发送给第三方镜像。

如需提高官方源的请求额度，可先运行一次 `hf auth login`，或在启动程序前设置可选的 `HF_TOKEN` 环境变量。程序不会将 Token 写入本地配置文件。

## 使用方法

### 无命令行窗口启动（Windows 推荐）

双击 `Start-WhisperGUI.vbs`。

### 从终端启动

```bash
python WhisperGUI.py
```

启动后选择 Whisper 模型、硬件设备和输出格式，添加媒体文件并开始转录。首次使用某个模型时，程序会自动下载对应文件。

## 模型存储与清理

模型统一保存在：

```text
./models/
```

模型与程序放在同一目录，方便整体移动到其他文件夹或移动硬盘。

需要释放空间时，可点击程序右上角的 **“卸载与清理”**，选择仅清理模型与缓存或彻底卸载。程序未运行时，也可以双击 `Uninstall.bat` 操作。

## 参与贡献

欢迎提交 Issue 和 Pull Request。后续可改进方向包括：

- 多语言转录与翻译流程
- 人声分离
- GUI 与交互体验优化

## 许可证

仓库目前未包含许可证文件。在添加明确许可证之前，源代码默认适用常规版权限制。
