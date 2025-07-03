import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
from matplotlib.widgets import LassoSelector


class LassoDataCleaner:
    def __init__(self, x_data, y_data, labels=None):
        """
        套索选择数据清洗工具
        
        Parameters:
        x_data: x轴数据
        y_data: y轴数据
        labels: 数据标签（可选）
        """
        self.x_original = np.array(x_data)
        self.y_original = np.array(y_data)
        self.labels = labels if labels is not None else range(len(x_data))
        
        self.x_current = self.x_original.copy()
        self.y_current = self.y_original.copy()
        self.current_labels = list(self.labels)
        
        self.selected_indices = []
        self.selector = None
        
        # 创建图形
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # 初始化绘图
        self.update_plots()
        self.setup_selector()
        
    def setup_selector(self):
        """设置套索选择器"""
        if self.selector:
            try:
                self.selector.disconnect_events()
            except:
                pass
        
        self.selector = LassoSelector(self.ax1, self.on_lasso_select)
    
    def on_lasso_select(self, verts):
        """套索选择回调函数"""
        if len(verts) < 3:
            return
            
        path = Path(verts)
        points = np.column_stack((self.x_current, self.y_current))
        self.selected_indices = [i for i, point in enumerate(points) if path.contains_point(point)]
        
        self.highlight_selected()
    
    def highlight_selected(self):
        """高亮显示选中的数据点"""
        self.ax1.clear()
        
        # 绘制未选中的点
        unselected = [i for i in range(len(self.x_current)) if i not in self.selected_indices]
        if unselected:
            self.ax1.scatter(self.x_current[unselected], self.y_current[unselected], 
                           c='lightgray', alpha=0.6, s=25)
        
        # 绘制选中的点
        if self.selected_indices:
            selected_x = self.x_current[self.selected_indices]
            selected_y = self.y_current[self.selected_indices]
            self.ax1.scatter(selected_x, selected_y, 
                           c='red', alpha=0.8, s=25, edgecolors='darkred')
        
        self.ax1.grid(True, alpha=0.3)
        
        # 重新设置选择器
        self.setup_selector()
        
        # 更新右图
        self.update_right_plot()
        
        plt.draw()
    
    def update_plots(self):
        """更新两个子图"""
        # 左图：当前数据
        self.ax1.clear()
        self.ax1.scatter(self.x_current, self.y_current, c='green', alpha=0.8, s=25)
        self.ax1.grid(True, alpha=0.3)
        
        # 右图：清洗后的数据
        self.update_right_plot()
        
        plt.tight_layout()
        plt.draw()
    
    def update_right_plot(self):
        """更新右侧图形"""
        self.ax2.clear()
        if len(self.selected_indices) > 0:
            selected_x = self.x_current[self.selected_indices]
            selected_y = self.y_current[self.selected_indices]
            self.ax2.scatter(selected_x, selected_y, c='blue', alpha=0.8, s=25)
        
        self.ax2.grid(True, alpha=0.3)
    
    def apply_cleaning(self):
        """应用数据清洗"""
        if not self.selected_indices:
            return False
        
        # 更新当前数据为选中的数据
        self.x_current = self.x_current[self.selected_indices]
        self.y_current = self.y_current[self.selected_indices]
        self.current_labels = [self.current_labels[i] for i in self.selected_indices]
        
        # 清空选择
        self.selected_indices = []
        
        # 更新图形
        self.update_plots()
        self.setup_selector()
        
        return True
    
    def reset_data(self):
        """重置为原始数据"""
        self.x_current = self.x_original.copy()
        self.y_current = self.y_original.copy()
        self.current_labels = list(self.labels)
        self.selected_indices = []
        
        self.update_plots()
        self.setup_selector()
    
    def get_cleaned_data(self):
        """获取当前清洗后的数据"""
        return self.x_current, self.y_current, self.current_labels
    
    def get_selected_count(self):
        """获取当前选中的数据点数量"""
        return len(self.selected_indices)
    
    def get_current_count(self):
        """获取当前数据点总数量"""
        return len(self.x_current)
