import os
import sys
import threading
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

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
        self.root.geometry("700x550")
        
        self.files = []
        self.is_running = False
        self.config_path = os.path.join(os.environ.get("USERPROFILE", ""), ".whisper_gui_config.json")
        
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
        
        # 第二行：按钮
        frame_row2 = ttk.Frame(frame_top)
        frame_row2.pack(fill=tk.X, pady=5)
        
        self.btn_select = ttk.Button(frame_row2, text="📂 1.选择视频文件", command=self.select_files)
        self.btn_select.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_start = ttk.Button(frame_row2, text="🚀 2.开始提取", command=self.start_processing)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_stop = ttk.Button(frame_row2, text="🛑 3.强制终止", command=self.stop_processing, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)
        
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
        print("⚠️ 如果初次运行某个级别的模型，会从 HuggingFace 自动下载模型文件，请耐心等待。")
        print("--------------------------------------------------\n")
        
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if "model" in cfg: self.model_var.set(cfg["model"])
                if "srt" in cfg: self.var_srt.set(cfg["srt"])
                if "vtt" in cfg: self.var_vtt.set(cfg["vtt"])
                if "txt" in cfg: self.var_txt.set(cfg["txt"])
                if "device" in cfg: self.device_var.set(cfg["device"])
        except Exception:
            pass

    def save_config(self):
        try:
            cfg = {
                "model": self.model_var.get(),
                "srt": self.var_srt.get(),
                "vtt": self.var_vtt.get(),
                "txt": self.var_txt.get(),
                "device": self.device_var.get()
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
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
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
        
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print("❌ 严重错误：找不到 faster-whisper 库，请确保运行环境正确！")
            self.restore_buttons()
            return
            
        try:
            model = WhisperModel(model_size, device=device_str, compute_type=compute_type_str)
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
        self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
