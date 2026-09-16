import os
import sys
import shutil
import subprocess
import threading
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

# ==========================================
# 软件路径基准定义 (绿色便携，本地化存放)
# ==========================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(APP_DIR, "models")

OFFICIAL_DOWNLOAD_SOURCE = "Hugging Face 官方源"
MIRROR_DOWNLOAD_SOURCE = "国内镜像 (hf-mirror.com)"
DOWNLOAD_SOURCES = {
    OFFICIAL_DOWNLOAD_SOURCE: "https://huggingface.co",
    MIRROR_DOWNLOAD_SOURCE: "https://hf-mirror.com",
}


def configure_hf_download_source(source_name):
    """Configure huggingface_hub before faster-whisper starts a download."""
    endpoint = DOWNLOAD_SOURCES.get(source_name, DOWNLOAD_SOURCES[OFFICIAL_DOWNLOAD_SOURCE])
    os.environ["HF_ENDPOINT"] = endpoint

    # huggingface_hub reads HF_ENDPOINT when it is imported. Update its cached
    # constants as well so switching sources still works later in the same run.
    try:
        from huggingface_hub import constants

        constants.ENDPOINT = endpoint
        constants.HUGGINGFACE_CO_URL_HOME = f"{endpoint}/"
        constants.HUGGINGFACE_CO_URL_TEMPLATE = (
            f"{endpoint}/{{repo_id}}/resolve/{{revision}}/{{filename}}"
        )
    except ImportError:
        pass

    return endpoint


def has_hf_auth_token():
    """Return whether huggingface_hub can find an environment or saved token."""
    try:
        from huggingface_hub import get_token

        return bool(get_token())
    except Exception:
        return bool(os.environ.get("HF_TOKEN"))

# ==========================================
# 自动加载 CUDA 核心组件库，彻底解决 0xc0000142 和 dll 报错
# ==========================================
try:
    import site
    site_packages = site.getsitepackages()
    cuda_paths = []
    for sp in site_packages:
        nvidia_base = os.path.join(sp, "nvidia")
        if os.path.exists(nvidia_base):
            for lib in ["cuda_runtime", "cublas", "cudnn", "cuda_nvrtc"]:
                bin_dir = os.path.join(nvidia_base, lib, "bin")
                if os.path.exists(bin_dir):
                    os.add_dll_directory(bin_dir)
                    cuda_paths.append(bin_dir)
    if cuda_paths:
        os.environ["PATH"] = ";".join(cuda_paths) + ";" + os.environ.get("PATH", "")
except Exception:
    pass

class RedirectText:
    def __init__(self, text_ctrl):
        self.output = text_ctrl
        
    def write(self, string):
        self.output.insert(tk.END, string)
        self.output.see(tk.END)
        
    def flush(self):
        pass

def format_timestamp(seconds: float, fmt: str = "srt") -> str:
    """将秒数转换为字幕时间戳格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    separator = "." if fmt == "vtt" else ","
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper视频字幕提取助手")
        self.root.geometry("720x610")
        
        self.files = []
        self.is_running = False
        self.config_path = os.path.join(APP_DIR, ".whisper_gui_config.json")
        
        # 顶部控制区
        frame_top = ttk.Frame(root, padding=10)
        frame_top.pack(fill=tk.X)
        
        # 第一行：模型、输出格式、设备
        frame_row1 = ttk.Frame(frame_top)
        frame_row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_row1, text="模型精度:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_var = tk.StringVar(value="large-v3")
        model_cb = ttk.Combobox(frame_row1, textvariable=self.model_var, values=["tiny", "base", "small", "medium", "large-v2", "large-v3"], state="readonly", width=8)
        model_cb.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(frame_row1, text="输出格式:").pack(side=tk.LEFT, padx=(0, 5))
        self.var_srt = tk.BooleanVar(value=True)
        self.var_vtt = tk.BooleanVar(value=False)
        self.var_txt = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(frame_row1, text="SRT", variable=self.var_srt).pack(side=tk.LEFT)
        ttk.Checkbutton(frame_row1, text="VTT", variable=self.var_vtt).pack(side=tk.LEFT)
        ttk.Checkbutton(frame_row1, text="TXT", variable=self.var_txt).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(frame_row1, text="计算设备:").pack(side=tk.LEFT, padx=(0, 5))
        self.device_var = tk.StringVar(value="GPU (cuda)")
        device_cb = ttk.Combobox(frame_row1, textvariable=self.device_var, values=["GPU (cuda)", "CPU (cpu)"], state="readonly", width=12)
        device_cb.pack(side=tk.LEFT)
        
        # 第二行：模型下载源
        frame_row2 = ttk.Frame(frame_top)
        frame_row2.pack(fill=tk.X, pady=5)

        ttk.Label(frame_row2, text="模型下载源:").pack(side=tk.LEFT, padx=(0, 5))
        self.download_source_var = tk.StringVar(value=OFFICIAL_DOWNLOAD_SOURCE)
        self.download_source_cb = ttk.Combobox(
            frame_row2,
            textvariable=self.download_source_var,
            values=list(DOWNLOAD_SOURCES.keys()),
            state="readonly",
            width=25,
        )
        self.download_source_cb.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(
            frame_row2,
            text="国内镜像无需 Token；官方源可选用 HF_TOKEN",
            foreground="#666666",
        ).pack(side=tk.LEFT)

        # 第三行：操作按钮与清理卸载
        frame_row3 = ttk.Frame(frame_top)
        frame_row3.pack(fill=tk.X, pady=5)
        
        self.btn_select = ttk.Button(frame_row3, text="📂 1.选择视频文件", command=self.select_files)
        self.btn_select.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_start = ttk.Button(frame_row3, text="🚀 2.开始提取", command=self.start_processing)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_stop = ttk.Button(frame_row3, text="🛑 3.强制终止", command=self.stop_processing, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_clean = ttk.Button(frame_row3, text="🗑️ 卸载与清理", command=self.open_clean_dialog)
        self.btn_clean.pack(side=tk.RIGHT)
        
        # 中间文件列表区
        frame_mid = ttk.Frame(root, padding=10)
        frame_mid.pack(fill=tk.X)
        ttk.Label(frame_mid, text="已选文件队列 (💡 支持直接拖拽视频文件到窗口):").pack(anchor=tk.W)
        self.listbox = tk.Listbox(frame_mid, height=4)
        self.listbox.pack(fill=tk.X, expand=True)
        
        try:
            import windnd
            windnd.hook_dropfiles(self.root, func=self.on_drop)
        except Exception:
            pass
        
        # 底部日志区
        frame_bot = ttk.Frame(root, padding=10)
        frame_bot.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame_bot, text="运行日志 / 进度监控:").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(frame_bot, height=15, state='normal', bg="black", fg="#00FF00", font=("Consolas", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # 重定向输出到界面文本框
        redir = RedirectText(self.log_area)
        sys.stdout = redir
        sys.stderr = redir
        
        print("💡 欢迎使用 Whisper 字幕助手！")
        print(f"📁 模型存放目录：{MODELS_DIR} (软件同级目录，绿色便携)")
        print("⚠️ 首次使用某个模型时，会从所选下载源自动下载文件到该目录，请耐心等待。")
        print("--------------------------------------------------\n")
        
        self.load_config()

    def load_config(self):
        try:
            cfg_path = self.config_path
            if not os.path.exists(cfg_path):
                legacy_path = os.path.join(os.environ.get("USERPROFILE", ""), ".whisper_gui_config.json")
                if os.path.exists(legacy_path):
                    cfg_path = legacy_path
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if "model" in cfg: self.model_var.set(cfg["model"])
                if "srt" in cfg: self.var_srt.set(cfg["srt"])
                if "vtt" in cfg: self.var_vtt.set(cfg["vtt"])
                if "txt" in cfg: self.var_txt.set(cfg["txt"])
                if "device" in cfg: self.device_var.set(cfg["device"])
                if cfg.get("download_source") in DOWNLOAD_SOURCES:
                    self.download_source_var.set(cfg["download_source"])
        except Exception:
            pass

    def save_config(self):
        try:
            cfg = {
                "model": self.model_var.get(),
                "srt": self.var_srt.get(),
                "vtt": self.var_vtt.get(),
                "txt": self.var_txt.get(),
                "device": self.device_var.get(),
                "download_source": self.download_source_var.get()
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
        except Exception:
            pass

    def select_files(self):
        filetypes = (
            ('常见媒体文件', '*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.flac *.m4a'),
            ('所有文件', '*.*')
        )
        filenames = filedialog.askopenfilenames(title='选择要处理的文件 (支持多选)', filetypes=filetypes)
        if filenames:
            self.files = list(filenames)
            self.listbox.delete(0, tk.END)
            for f in self.files:
                self.listbox.insert(tk.END, os.path.basename(f))
            print(f"📁 已选择 {len(self.files)} 个文件。")

    def on_drop(self, files):
        if self.is_running:
            messagebox.showwarning("提示", "正在处理中，请先停止任务后再拖入文件！")
            return
            
        count = 0
        for f in files:
            try:
                path = f.decode("gbk")
            except Exception:
                path = f.decode("utf-8", errors="ignore")
                
            if os.path.isfile(path) and path not in self.files:
                self.files.append(path)
                self.listbox.insert(tk.END, os.path.basename(path))
                count += 1
                
        if count > 0:
            print(f"📁 拖拽追加了 {count} 个文件，当前共 {len(self.files)} 个待处理。")

    def start_processing(self):
        if not self.files:
            messagebox.showwarning("提示", "请先选择需要处理的视频/音频文件！")
            return
            
        self.save_config()
        self.active_download_source = self.download_source_var.get()
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
        self.download_source_cb.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.is_running = True
        
        # 在新线程中运行核心处理逻辑，防止界面卡死
        threading.Thread(target=self.process_files, daemon=True).start()
        
    def stop_processing(self):
        if self.is_running:
            self.is_running = False
            self.btn_stop.config(state=tk.DISABLED)
            print("\n🛑 收到强制终止指令，正在停止当前任务...")
        
    def process_files(self):
        model_size = self.model_var.get()
        device_choice = self.device_var.get()
        download_source = self.active_download_source
        device_str = "cuda" if "GPU" in device_choice else "cpu"
        compute_type_str = "float16" if device_str == "cuda" else "int8"
        
        selected_formats = []
        if self.var_srt.get(): selected_formats.append("srt")
        if self.var_vtt.get(): selected_formats.append("vtt")
        if self.var_txt.get(): selected_formats.append("txt")
        if not selected_formats:
            selected_formats = ["srt"] # 默认兜底
        
        print(f"\n==================================================")
        print(f"▶️ 正在召唤 {device_str.upper()} 加载【{model_size}】模型 (初次约需几秒至几分钟下载)...")
        print(f"📁 模型存储路径: {MODELS_DIR}")
        endpoint = configure_hf_download_source(download_source)
        print(f"🌐 模型下载源: {download_source} ({endpoint})")
        if download_source == OFFICIAL_DOWNLOAD_SOURCE:
            if has_hf_auth_token():
                print("🔐 已检测到 Hugging Face 登录凭据，将使用登录额度下载。")
            else:
                print("ℹ️ 未检测到登录凭据：公开模型仍可正常匿名下载，相关 Warning 仅表示限速。")
        else:
            print("ℹ️ 国内镜像模式不会向第三方镜像发送 HF_TOKEN。")
        
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print("❌ 严重错误：找不到 faster-whisper 库，请确保运行环境正确！")
            self.restore_buttons()
            return
            
        try:
            os.makedirs(MODELS_DIR, exist_ok=True)
            model = WhisperModel(
                model_size,
                device=device_str,
                compute_type=compute_type_str,
                download_root=MODELS_DIR,
                use_auth_token=False if download_source == MIRROR_DOWNLOAD_SOURCE else None,
            )
            print(f"✅ 模型加载成功！{device_str.upper()} 已就绪！")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.restore_buttons()
            return

        for idx, file_path in enumerate(self.files):
            if not self.is_running:
                break
            file_name = os.path.basename(file_path)
            
            # 更新列表 UI 显示正在处理
            self.root.after(0, lambda i=idx, f=file_name: self.update_listbox_item(i, f"▶️ {f} (处理中...)"))
            
            print(f"\n🎬 开始处理视频: {file_name}")
            try:
                # beam_size=5 可以在速度和准确度中取得非常好的平衡
                segments, info = model.transcribe(file_path, beam_size=5)
                print(f"🔍 识别到视频主要语言为: '{info.language}' (置信度: {info.language_probability:.2f})")
                print("⏳ 正在逐句提取字幕，请看进度：\n")
                
                base_name = os.path.splitext(file_path)[0]
                out_files = {}
                for fmt in selected_formats:
                    f = open(base_name + f".{fmt}", "w", encoding="utf-8")
                    if fmt == "vtt":
                        f.write("WEBVTT\n\n")
                    out_files[fmt] = f
                
                for i, segment in enumerate(segments, start=1):
                    if not self.is_running:
                        print("\n🛑 提取过程已被强制打断！")
                        break
                        
                    text = segment.text.strip()
                    
                    if "srt" in out_files:
                        start_str = format_timestamp(segment.start, "srt")
                        end_str = format_timestamp(segment.end, "srt")
                        out_files["srt"].write(f"{i}\n{start_str} --> {end_str}\n{text}\n\n")
                        
                    if "vtt" in out_files:
                        start_str = format_timestamp(segment.start, "vtt")
                        end_str = format_timestamp(segment.end, "vtt")
                        out_files["vtt"].write(f"{i}\n{start_str} --> {end_str}\n{text}\n\n")
                        
                    if "txt" in out_files:
                        out_files["txt"].write(f"{text}\n")
                        
                    # 实时进度只需打印一次
                    start_disp = format_timestamp(segment.start, "srt")
                    end_disp = format_timestamp(segment.end, "srt")
                    print(f"[{start_disp} -> {end_disp}] {text}")
                    
                # 关闭所有打开的文件句柄
                for f in out_files.values():
                    f.close()
                    
                if not self.is_running:
                    self.root.after(0, lambda i=idx, f=file_name: self.update_listbox_item(i, f"🛑 {f} (已终止)"))
                    break
                        
                print(f"\n✅ 视频 {file_name} 字幕提取完美收工！已保存至旁边。")
                # 更新列表 UI 显示完成
                self.root.after(0, lambda i=idx, f=file_name: self.update_listbox_item(i, f"✅ {f}"))
            except Exception as e:
                print(f"\n❌ 处理文件 {file_name} 时发生错误: {e}")
                # 更新列表 UI 显示错误
                self.root.after(0, lambda i=idx, f=file_name: self.update_listbox_item(i, f"❌ {f} (失败)"))

        if self.is_running:
            print("\n🎉 所有队列任务均已全部完成！辛苦显卡了~")
        else:
            print("\n⚠️ 任务已全部安全终止。")
            
        self.restore_buttons()
        
    def update_listbox_item(self, index, new_text):
        """线程安全的更新列表框某一项的文本"""
        self.listbox.delete(index)
        self.listbox.insert(index, new_text)
        
    def restore_buttons(self):
        # 恢复按钮为可点击状态 (必须回调到主线程安全更新)
        self.is_running = False
        self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.btn_select.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.download_source_cb.config(state="readonly"))
        self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))

    def get_dir_size_str(self, path):
        """计算指定目录的总文件大小并格式化为字符串"""
        if not os.path.exists(path):
            return "0 MB (未下载)"
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        if total_size == 0:
            return "0 MB"
        elif total_size < 1024 * 1024:
            return f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            return f"{total_size / (1024 * 1024):.1f} MB"
        else:
            return f"{total_size / (1024 * 1024 * 1024):.2f} GB"

    def open_clean_dialog(self):
        """打开数据清理与卸载管理对话框"""
        if self.is_running:
            messagebox.showwarning("提示", "当前有任务正在运行中，请先停止任务后再进行清理！")
            return

        clean_win = tk.Toplevel(self.root)
        clean_win.title("数据清理与卸载")
        clean_win.geometry("460x280")
        clean_win.resizable(False, False)
        clean_win.transient(self.root)
        clean_win.grab_set()

        models_size_str = self.get_dir_size_str(MODELS_DIR)

        pad_frame = ttk.Frame(clean_win, padding=20)
        pad_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(pad_frame, text="🧹 数据清理与卸载管理", font=("", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        info_text = (
            f"• 模型存放目录: ./models/\n"
            f"• 当前模型占用: {models_size_str}\n"
            f"• 本地配置文件: .whisper_gui_config.json\n\n"
            f"提示：所有模型均下载在当前软件同级目录下，不会污染系统 C 盘。"
        )
        ttk.Label(pad_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))

        def do_clean_cache():
            if messagebox.askyesno("确认清理", "确定要清空已下载的模型文件、配置文件与运行缓存吗？\n\n（操作将释放磁盘空间，软件仍可正常使用）", parent=clean_win):
                clean_win.destroy()
                self.clean_generated_files()

        def do_uninstall_all():
            if messagebox.askyesno("确认彻底卸载", "⚠️ 警告：彻底卸载将清空所有已下载模型、配置文件，并在退出程序后自动删除本软件所有文件！\n\n确定要继续彻底卸载吗？", parent=clean_win):
                clean_win.destroy()
                self.uninstall_all_files()

        btn_frame = ttk.Frame(pad_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="🗑️ 仅清理模型与缓存 (释放磁盘)", command=do_clean_cache).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="💥 彻底卸载本软件 (删除所有文件)", command=do_uninstall_all).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="取消", command=clean_win.destroy).pack(fill=tk.X, pady=3)

    def clean_generated_files(self):
        """一键清理软件产生的所有文件（模型、配置、缓存）"""
        print("\n==================================================")
        print("🧹 正在开始清理已产生的数据与缓存...")
        
        # 1. 删除 models 目录
        if os.path.exists(MODELS_DIR):
            try:
                shutil.rmtree(MODELS_DIR)
                print(f"✅ 已清空本地模型目录: {MODELS_DIR}")
            except Exception as e:
                print(f"❌ 删除模型目录失败: {e}")
        else:
            print("ℹ️ 本地模型目录为空，无需清理。")

        # 2. 删除配置文件
        for cfg in [self.config_path, os.path.join(os.environ.get("USERPROFILE", ""), ".whisper_gui_config.json")]:
            if os.path.exists(cfg):
                try:
                    os.remove(cfg)
                    print(f"✅ 已删除配置文件: {cfg}")
                except Exception as e:
                    print(f"❌ 删除配置文件失败: {e}")

        # 3. 删除 __pycache__
        pycache_dir = os.path.join(APP_DIR, "__pycache__")
        if os.path.exists(pycache_dir):
            try:
                shutil.rmtree(pycache_dir)
                print(f"✅ 已清理 Python 缓存: {pycache_dir}")
            except Exception as e:
                pass

        print("🎉 缓存与模型文件已清理完毕，磁盘空间已释放！\n==================================================\n")
        messagebox.showinfo("提示", "模型文件与配置文件已全部清理完成，磁盘空间已释放！")

    def uninstall_all_files(self):
        """彻底卸载本软件并自清理"""
        print("\n==================================================")
        print("⚠️ 正在准备彻底卸载本软件...")
        
        # 1. 先清理生成文件
        if os.path.exists(MODELS_DIR):
            shutil.rmtree(MODELS_DIR, ignore_errors=True)
        for cfg in [self.config_path, os.path.join(os.environ.get("USERPROFILE", ""), ".whisper_gui_config.json")]:
            if os.path.exists(cfg):
                try: os.remove(cfg)
                except Exception: pass
        pycache_dir = os.path.join(APP_DIR, "__pycache__")
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir, ignore_errors=True)

        # 2. 调度自删除命令并退出
        cmd = f'cmd.exe /c (ping 127.0.0.1 -n 3 > nul & rd /s /q "{APP_DIR}")'
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        messagebox.showinfo("卸载完成", "已完成清理，软件目录将在程序退出后自动删除。")
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
