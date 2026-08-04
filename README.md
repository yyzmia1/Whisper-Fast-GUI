这里为你重写了一版更加规范、客观的开发者文档风格 README，去除了原本过于夸张的营销词汇和冗余的 Emoji：

```markdown
# Whisper-Fast-GUI

Whisper-Fast-GUI 是一个基于 `faster-whisper` 的轻量级音视频字幕提取桌面工具。其图形用户界面（GUI）完全使用 Python 内置的 `tkinter` 库编写，无需额外安装复杂的 GUI 框架。

## 主要特性

- **轻量化**：界面纯 Python 标准库编写，主逻辑集中于单文件。
- **硬件加速**：底层基于 CTranslate2 + faster-whisper，支持 GPU 加速提取。
- **文件拖拽**：支持直接将音视频文件拖入软件窗口并自动加入处理队列。
- **配置保存**：自动记忆上次使用的模型精度、输出格式和硬件设备。
- **多格式导出**：支持同时输出 SRT、VTT 和 TXT 格式。
- **任务管理**：支持在处理过程中强制终止任务，并正常释放硬件资源。
- **静默运行**：提供 Windows 下的 `.vbs` 脚本，可隐藏命令行（CMD）窗口启动。

## 环境依赖与安装

请确保系统已安装 Python 3.9 或更高版本。在项目根目录下执行以下命令安装依赖：

```bash
pip install -r requirements.txt

```

**Windows NVIDIA 显卡用户注意：**
如果默认 Python 环境在加载 faster-whisper 时提示 `cublas64_12.dll is not found` 或报 `0xc0000142` 错误，说明系统缺少 CUDA 运行库。
若未安装完整的 PyTorch 环境，可通过执行以下命令补充所需依赖（源码已内置驱动寻址，无需手动配置环境变量）：

```bash
pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12

```

## 启动方式

**方式一：无命令行窗口启动（仅限 Windows，推荐）**
双击根目录下的 `Start-WhisperGUI.vbs` 文件，软件将以无命令行窗口的形式启动。

**方式二：命令行启动**
在终端或命令行中执行：

```bash
python WhisperGUI.py

```

## 参与贡献

欢迎对本项目提交 Pull Request。目前计划或希望改进的方向包括：

* 增加多语言识别与翻译支持
* 引入人声分离功能
* GUI 界面与交互逻辑优化

```

```
