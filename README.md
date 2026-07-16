# Whisper-Fast-GUI

一个基于 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 的极简、高效、无黑框的视频字幕提取桌面工具。

完全使用 Python 内置库 `tkinter` 编写，无冗余的重型框架，点击即用，榨干显卡算力！

## ✨ 核心特性

- **🚀 极致轻量**：纯 Python 标准库编写 GUI，代码仅一个单文件。
- **⚡️ 性能拉满**：底层使用 CTranslate2 + faster-whisper，支持 GPU 加速提取，速度远超原版 Whisper。
- **📥 完美拖拽支持**：支持批量将视频、音频直接拖拽进窗口排队提取。
- **💾 习惯记忆系统**：自动记忆你上次选择的模型精度、输出格式、硬件设备。
- **🗂️ 多种格式并发输出**：支持同时输出 `SRT`、`VTT`、`TXT`，提取一次，全格式拿走。
- **🛑 随时强制终止**：任务中断自由，点击终止瞬间释放资源，绝不卡死。
- **👻 无痕启动**：告别繁杂丑陋的 CMD 黑框，提供 `.vbs` 隐身启动方案。

## 📦 依赖安装

在使用之前，请确保你已经安装了 Python 环境（推荐 Python 3.9+），并执行以下命令安装核心依赖：

```bash
pip install -r requirements.txt
```

> **注意：NVIDIA 显卡用户 (Windows)**  
> 默认的 Python 环境可能在加载 `faster-whisper` 时提示 `cublas64_12.dll is not found or cannot be loaded` 或 `0xc0000142` 错误。
> 这是因为缺少系统级的 CUDA 运行库。如果你没有安装庞大的 PyTorch，你可以通过执行以下命令完美补全：
> ```bash
> pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12
> ```
> *(本源码已在顶部内置了底层驱动寻址注入，只要按上述安装好依赖，无需配置系统环境变量即可完美点亮 CUDA！)*

## 🚀 启动方式

### 方式一：一键无黑框启动（推荐）
直接双击文件夹内的 **`一键启动(无黑框).vbs`** 文件，软件会瞬间在桌面展现，背后毫无 CMD 黑框残留，体验如原生原生独立软件一般顺滑。

### 方式二：命令行启动
```bash
python WhisperGUI.py
```

## 📝 贡献
这是一个为极致简约与效率而诞生的开源小玩具。如果你有关于增加多语言支持、人声分离分离、或界面优化的想法，欢迎提交 Pull Request！
