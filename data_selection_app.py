import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from lasso_selector import LassoDataCleaner


class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据精选工具")
        
        self.cleaner = None
        self.canvas = None
        
        self.setup_ui()
        self.load_demo_data()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮
        ttk.Button(control_frame, text="加载数据", command=self.load_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="应用选择", command=self.apply_cleaning).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="重置数据", command=self.reset_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="保存数据", command=self.save_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # 信息显示
        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(control_frame, textvariable=self.info_var)
        self.info_label.pack(side=tk.RIGHT)
        
        # 图形显示区域
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def load_demo_data(self):
        """加载演示数据"""
        np.random.seed(42)
        n_points = 200
        
        # 主要数据集群
        main_x = np.random.normal(5, 1.5, int(n_points * 0.7))
        main_y = np.random.normal(3, 1.2, int(n_points * 0.7))
        
        # 离群点
        outlier_x = np.random.uniform(0, 12, int(n_points * 0.3))
        outlier_y = np.random.uniform(-2, 8, int(n_points * 0.3))
        
        # 合并数据
        x_data = np.concatenate([main_x, outlier_x])
        y_data = np.concatenate([main_y, outlier_y])
        
        self.create_cleaner(x_data, y_data)
        self.status_var.set("已加载演示数据")
    
    def read_csv_with_numpy(file_path):
        """
        使用 NumPy 读取 CSV 文件的前两列（x, y），可选第三列为标签
        """
        try:
            # 尝试读取最多三列
            data = np.genfromtxt(file_path, delimiter=',', skip_header=1, dtype=str)
            if data.ndim == 1:
                raise ValueError("CSV 文件内容格式有误，必须至少包含两列")

            if data.shape[1] < 2:
                raise ValueError("CSV 文件必须至少包含两列")

            x_data = data[:, 0].astype(float)
            y_data = data[:, 1].astype(float)

            if data.shape[1] >= 3:
                labels = data[:, 2].tolist()
            else:
                labels = [str(i) for i in range(len(x_data))]

            return x_data, y_data, labels

        except Exception as e:
            raise ValueError(f"无法读取 CSV 文件: {e}")
    
    
    def load_data(self):
        """加载数据文件"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[
                ("逗号分隔值", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            x_data, y_data, labels = read_csv_with_numpy(file_path)
            self.create_cleaner(x_data, y_data, labels)
            self.status_var.set(f"已加载数据文件: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def create_cleaner(self, x_data, y_data, labels=None):
        """创建数据清洗器"""
        # 清除之前的画布
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # 创建清洗器
        self.cleaner = LassoDataCleaner(x_data, y_data, labels)
        
        # 嵌入matplotlib图形
        self.canvas = FigureCanvasTkAgg(self.cleaner.fig, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        
        # 更新信息
        self.update_info()
    
    def apply_cleaning(self):
        """应用数据清洗"""
        if not self.cleaner:
            messagebox.showwarning("警告", "请先加载数据")
            return
        
        if self.cleaner.get_selected_count() == 0:
            messagebox.showwarning("警告", "请先选择数据点")
            return
        
        success = self.cleaner.apply_cleaning()
        if success:
            self.update_info()
            self.canvas.draw()
            self.status_var.set("数据已精选！")
        else:
            messagebox.showerror("错误", "应用清洗失败")
    
    def reset_data(self):
        """重置数据"""
        if not self.cleaner:
            messagebox.showwarning("警告", "请先加载数据")
            return
        
        self.cleaner.reset_data()
        self.update_info()
        self.canvas.draw()
        self.status_var.set("已重置数据")
    
    def save_data(self):
        """保存数据"""
        if not self.cleaner:
            messagebox.showwarning("警告", "请先加载数据")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存清洗后的数据",
            defaultextension=".csv",
            filetypes=[
                ("逗号分隔值", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            x, y, labels = self.cleaner.get_cleaned_data()
            arr = np.column_stack((x, y, labels))
            header = "x,y,label"
            np.savetxt(file_path, arr, delimiter=',', fmt='%s', header=header, comments='')

            messagebox.showinfo("成功", f"数据已保存到: {file_path}")
            self.status_var.set(f"数据已保存到: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def update_info(self):
        """更新信息显示"""
        if self.cleaner:
            current_count = self.cleaner.get_current_count()
            selected_count = self.cleaner.get_selected_count()
            info_text = f"当前数据: {current_count} 个点"
            if selected_count > 0:
                info_text += f" | 已选择: {selected_count} 个点"
            self.info_var.set(info_text)

def main():
    """主函数"""
    root = tk.Tk()
    DataCleanerApp(root)
    
    # 设置窗口关闭事件
    def on_closing():
        try:
            plt.close('all')
        except Exception as e:
            messagebox.showerror("错误", str(e))
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
