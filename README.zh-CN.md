# Whisper-Fast-GUI

[English](README.md) | **简体中文**

在自己的 Windows 电脑上，把音频和视频快速转换成字幕文件。

Whisper-Fast-GUI 为
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) 提供了一个简单的桌面界面。添加文件、选择模型并开始处理，全程无需把音视频上传到在线转录服务。

## 为什么选择它？

- **本地处理，更保护隐私**：转录过程在你的电脑上完成。
- **支持批量操作**：可以多选文件，也可以直接拖入窗口。
- **常用格式齐全**：支持导出 SRT、VTT 和纯文本 TXT。
- **CPU 与 NVIDIA GPU 均可使用**：没有独立显卡也能运行。
- **适配国内网络**：可在 Hugging Face 官方源和 `hf-mirror.com` 国内镜像之间切换。
- **绿色便携**：模型和配置保存在软件目录中，方便移动与清理。

常见音视频格式包括 MP4、AVI、MKV、MOV、MP3、WAV、FLAC 和 M4A。

## 使用前准备

你需要：

- Windows 电脑
- Python 3.9 或更高版本
- 首次下载每个模型时需要联网
- NVIDIA 显卡不是必需品；没有显卡可以选择 CPU 模式

> [!NOTE]
> 当前项目提供的是源码版本，还没有预先打包好的 `.exe` 安装程序。因此首次使用前需要安装 Python。

## 四步开始使用

### 第一步：下载项目

[点击下载最新 ZIP](https://github.com/yyzmiao/Whisper-Fast-GUI/archive/refs/heads/main.zip)，
解压到一个空间充足的文件夹。后续下载的 Whisper 模型也会保存在这里。

### 第二步：安装 Python

安装 Python 3.9 或更高版本。在 Windows 安装界面中，请勾选
**Add python.exe to PATH**。

### 第三步：安装运行依赖

在解压后的项目文件夹中打开终端，执行：

```powershell
python -m pip install -r requirements.txt
```

### 第四步：启动软件

双击：

```text
Start-WhisperGUI.vbs
```

软件会直接显示图形界面，不会留下命令行黑框。也可以在终端中执行 `python WhisperGUI.py` 启动。

## 如何生成字幕

1. 选择模型，再选择 **GPU** 或 **CPU**。
2. 勾选需要的输出格式：**SRT**、**VTT** 和/或 **TXT**。
3. 选择模型下载源。国内网络无法稳定访问官方源时，可选择国内镜像。
4. 点击 **“1. 选择视频文件”**，或把文件直接拖入窗口。
5. 点击 **“2. 开始提取”**。

生成的字幕文件会保存在原音视频文件旁边。

## 模型应该怎么选？

| 模型 | 适合场景 | 取舍 |
| --- | --- | --- |
| `tiny` / `base` | 快速预览、配置较旧的电脑 | 速度最快，准确率相对较低 |
| `small` | CPU 用户的实用起点 | 速度和准确率比较均衡 |
| `medium` | 硬件较好，希望提高准确率 | 更慢、占用更多内存 |
| `large-v3` | 追求软件当前支持的最佳准确率 | 推荐使用性能较好的 NVIDIA 显卡 |

每个模型第一次使用时都需要下载，所以首次运行会慢一些。以后会直接复用 `./models/` 中已经下载的文件。

## 下载源与 `HF_TOKEN` 提示

- **Hugging Face 官方源**是默认选项。公开模型无需账号也能下载。出现未认证请求的 Warning 并不代表出错，只表示匿名请求的速率额度较低。
- **国内镜像（`hf-mirror.com`）**适合官方源速度慢或无法访问的情况。软件不会把 Hugging Face Token 发送给这个第三方镜像。

登录不是必需的。如果希望提高官方源的请求额度，可以执行一次：

```powershell
hf auth login
```

按提示完成登录即可。也可以在启动软件前设置 `HF_TOKEN` 环境变量。Token 不会写入 `.whisper_gui_config.json`。

## 常见问题

### 第一次转录看起来一直没有反应

程序可能仍在下载所选模型。模型越大，下载时间和占用空间越多。请观察软件底部日志，看到模型加载成功后才会开始正式转录。

### 出现 `cublas64_12.dll is not found` 或 `0xc0000142`

安装可选的 NVIDIA CUDA 运行库：

```powershell
python -m pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12
```

安装完成后重启软件。如果不需要显卡加速，也可以直接选择 CPU 模式。

### 下载的模型保存在哪里？

模型保存在项目目录下的 `models` 文件夹中，不会使用 Hugging Face 默认的系统盘缓存目录。

### 如何释放模型占用的空间？

点击软件右上角的 **“🗑️ 卸载与清理”**。软件关闭时，也可以运行 `Uninstall.bat`。

### 音视频会上传到网络吗？

不会。音视频转录完全在本地运行，网络只用于下载模型文件。

## 开发者使用

```powershell
git clone https://github.com/yyzmiao/Whisper-Fast-GUI.git
cd Whisper-Fast-GUI
python -m pip install -r requirements.txt
python WhisperGUI.py
```

欢迎提交 Issue 和 Pull Request。

## 许可证

仓库目前未包含许可证文件。在添加明确许可证之前，源代码默认适用常规版权限制。
