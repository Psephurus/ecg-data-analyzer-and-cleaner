import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


class ECGAnalyzer:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("ECG数据分析器")
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="ECG数据分析器", 
                   font=('Microsoft YaHei', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="15")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="ECG文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, 
                                   state='readonly', width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="浏览", 
                  command=self.browse_file).grid(row=0, column=2)
        
        # 参数设置区域
        params_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="15")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 采样频率
        ttk.Label(params_frame, text="采样频率 (Hz):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.fs_var = tk.StringVar(value="500")
        fs_entry = ttk.Entry(params_frame, textvariable=self.fs_var, width=10)
        fs_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 滤波参数
        ttk.Label(params_frame, text="带通滤波 (Hz):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        filter_frame = ttk.Frame(params_frame)
        filter_frame.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        self.lowcut_var = tk.StringVar(value="1")
        self.highcut_var = tk.StringVar(value="45")
        
        ttk.Entry(filter_frame, textvariable=self.lowcut_var, width=8).pack(side=tk.LEFT)
        ttk.Label(filter_frame, text=" - ").pack(side=tk.LEFT)
        ttk.Entry(filter_frame, textvariable=self.highcut_var, width=8).pack(side=tk.LEFT)
        
        # 处理和保存按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 15))
        
        self.process_btn = ttk.Button(button_frame, text="处理并保存", 
                                     command=self.process_and_save, 
                                     style='Accent.TButton')
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="退出", 
                  command=self.root.quit).pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态和日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="15")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择ECG数据文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log_message(f"已选择文件: {os.path.basename(file_path)}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def load_ecg_data(self, filepath):
        """加载ECG数据"""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"未找到文件: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            next(file)  # 跳过表头
            adc_values = []
            for line_num, line in enumerate(file, 2):
                try:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        adc_values.append(int(parts[1]))
                except (ValueError, IndexError) as e:
                    self.log_message(f"警告: 第{line_num}行数据格式错误，已跳过")
        
        if not adc_values:
            raise ValueError("文件中没有有效的ECG数据")
        
        return adc_values
    
    def bandpass_filter(self, signal, fs, lowcut=1, highcut=45, order=4):
        """带通滤波"""
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, signal)
    
    def detect_r_peaks(self, ecg_signal, fs):
        """检测R峰"""
        peaks, _ = find_peaks(
            ecg_signal,
            height=np.percentile(ecg_signal, 90),
            distance=int(0.25 * fs),
            prominence=np.std(ecg_signal) * 0.8
        )
        
        # 计算RR间期（秒）
        rr_intervals = np.diff(peaks) / fs
        self.log_message(f"检测到 {len(peaks)} 个R峰，{len(rr_intervals)} 个RR间期")
        return rr_intervals
    
    def save_rr_intervals(self, rr_intervals, filepath):
        """保存RR间期对"""
        if len(rr_intervals) == 0:
            self.log_message("警告: 没有RR间期数据可保存")
            return
        
        # 构造 (RR[n], RR[n+1]) 的二维数组
        rr_pairs = np.column_stack((rr_intervals[:-1], rr_intervals[1:]))
        np.savetxt(filepath, rr_pairs, delimiter=',', 
                  header='RR(n),RR(n+1)', comments='', fmt='%.6f')
        self.log_message(f"已保存 {len(rr_pairs)} 对RR间期到: {os.path.basename(filepath)}")
    
    def process_and_save(self):
        if not self.file_path_var.get():
            messagebox.showwarning("错误", "请先选择ECG数据文件")
            return
        
        try:
            # 获取参数
            fs = float(self.fs_var.get())
            lowcut = float(self.lowcut_var.get())
            highcut = float(self.highcut_var.get())
            
            if fs <= 0 or lowcut <= 0 or highcut <= lowcut:
                raise ValueError("参数设置不正确")
            
        except ValueError as e:
            messagebox.showerror("参数错误", "请检查参数设置是否正确")
            return
        
        # 开始处理
        self.process_btn.config(state='disabled')
        self.progress.start(10)
        
        try:
            input_path = self.file_path_var.get()
            self.log_message("=" * 50)
            self.log_message(f"开始处理文件: {os.path.basename(input_path)}")
            
            # 加载数据
            self.log_message("正在加载ECG数据...")
            ecg_data = self.load_ecg_data(input_path)
            self.log_message(f"成功加载 {len(ecg_data)} 个数据点")
            
            # 转换为numpy数组并滤波
            self.log_message("正在进行带通滤波...")
            ecg_signal = np.array(ecg_data, dtype=float)
            filtered_signal = self.bandpass_filter(ecg_signal, fs, lowcut, highcut)
            self.log_message(f"滤波完成 (频率范围: {lowcut}-{highcut} Hz)")
            
            # 检测R峰
            self.log_message("正在检测R峰...")
            rr_intervals = self.detect_r_peaks(filtered_signal, fs)
            
            if len(rr_intervals) < 2:
                raise ValueError("检测到的R峰数量不足，无法生成RR间期对")
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            default_name = f"{base_name}_RR_intervals.csv"
            
            # 选择保存位置
            output_path = filedialog.asksaveasfilename(
                title="保存RR间期文件",
                defaultextension=".csv",
                initialfile=default_name,
                filetypes=[("逗号分隔值文件", "*.csv"), ("所有文件", "*.*")]
            )
            
            if not output_path:
                self.log_message("用户取消了保存操作")
                return
            
            # 保存结果
            self.log_message("正在保存RR间期数据...")
            self.save_rr_intervals(rr_intervals, output_path)
            
            # 显示统计信息
            self.log_message(f"RR间期统计:")
            self.log_message(f"  平均值: {np.mean(rr_intervals):.3f} 秒")
            self.log_message(f"  标准差: {np.std(rr_intervals):.3f} 秒")
            self.log_message(f"  范围: {np.min(rr_intervals):.3f} - {np.max(rr_intervals):.3f} 秒")
            self.log_message("处理完成！")
            
            messagebox.showinfo("处理完成", f"ECG数据处理完成！\n输出文件: {os.path.basename(output_path)}")
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("处理错误", error_msg)
        
        finally:
            self.progress.stop()
            self.process_btn.config(state='normal')
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ECGAnalyzer()
    app.run()
