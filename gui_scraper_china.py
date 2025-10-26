#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全国艺术培训机构数据采集系统 - 全国版
支持全国34个省级行政区的所有城市
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import time
import json
import pandas as pd
from openpyxl import Workbook
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from shandong_training_scraper import ShandongTrainingScraper

class ChinaScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("全国艺术培训机构数据采集系统 - 全国版")
        self.root.geometry("1000x750")
        
        self.is_running = False
        self.config_file = "scraper_config.json"
        
        # 从JSON文件加载全国城市
        self.load_china_cities()
        
        # 预设专业关键词库（大幅扩展）
        self.preset_keywords = {
            # 声乐类
            '声乐': ['声乐培训', '唱歌培训', '声乐教学', '声乐艺术', '声乐班', '歌唱培训', '声乐学校', '声乐中心', '唱歌班', 'K歌培训', '流行演唱', '美声培训', '民族唱法', '声乐工作室', '歌唱艺术'],
            
            # 西洋乐器类
            '钢琴': ['钢琴培训', '钢琴教学', '钢琴班', '钢琴学校', '钢琴教室', '钢琴艺术', '钢琴中心', '学钢琴', '钢琴课程', '钢琴工作室', '钢琴速成', '钢琴陪练'],
            '小提琴': ['小提琴培训', '小提琴教学', '小提琴班', '小提琴学校', '小提琴教室', '小提琴艺术', '学小提琴', '小提琴课程'],
            '大提琴': ['大提琴培训', '大提琴教学', '大提琴班', '大提琴学校', '大提琴教室', '学大提琴'],
            '架子鼓': ['架子鼓培训', '架子鼓教学', '架子鼓班', '架子鼓学校', '架子鼓教室', '学架子鼓', '爵士鼓培训', '打鼓培训'],
            '萨克斯': ['萨克斯培训', '萨克斯教学', '萨克斯班', '萨克斯学校', '萨克斯教室', '学萨克斯', '萨克斯风培训'],
            '长笛': ['长笛培训', '长笛教学', '长笛班', '长笛学校', '长笛教室', '学长笛'],
            '吉他': ['吉他培训', '吉他教学', '吉他班', '吉他学校', '吉他教室', '民谣吉他', '电吉他', '古典吉他', '吉他艺术', '吉他中心', '学吉他', '吉他课程', '吉他工作室', '尤克里里培训'],
            
            # 民族乐器类
            '古筝': ['古筝培训', '古筝教学', '古筝班', '古筝学校', '古筝教室', '古筝艺术', '古筝中心', '古筝学习', '古筝课程', '学古筝', '古筝工作室'],
            '二胡': ['二胡培训', '二胡教学', '二胡班', '二胡学校', '二胡教室', '二胡艺术', '二胡中心', '民乐培训', '学二胡', '二胡课程'],
            '琵琶': ['琵琶培训', '琵琶教学', '琵琶班', '琵琶学校', '琵琶教室', '琵琶艺术', '学琵琶', '琵琶课程'],
            '竹笛': ['竹笛培训', '竹笛教学', '竹笛班', '竹笛学校', '竹笛教室', '笛子培训', '学竹笛', '笛子教学'],
            '葫芦丝': ['葫芦丝培训', '葫芦丝教学', '葫芦丝班', '葫芦丝学校', '葫芦丝教室', '学葫芦丝'],
            '扬琴': ['扬琴培训', '扬琴教学', '扬琴班', '扬琴学校', '学扬琴'],
            
            # 舞蹈类
            '舞蹈': ['舞蹈培训', '舞蹈学校', '舞蹈教学', '舞蹈班', '舞蹈中心', '舞蹈艺术', '舞蹈教室', '舞蹈工作室', '艺术舞蹈', '少儿舞蹈'],
            '芭蕾舞': ['芭蕾舞培训', '芭蕾舞教学', '芭蕾舞班', '芭蕾舞学校', '芭蕾舞教室', '芭蕾舞蹈', '学芭蕾', '芭蕾课程'],
            '拉丁舞': ['拉丁舞培训', '拉丁舞教学', '拉丁舞班', '拉丁舞学校', '拉丁舞教室', '拉丁舞中心', '国标舞', '拉丁舞艺术', '体育舞蹈', '学拉丁舞'],
            '民族舞': ['民族舞培训', '民族舞教学', '民族舞班', '民族舞学校', '民族舞教室', '中国舞', '民族舞蹈', '民族舞艺术', '古典舞培训', '民族民间舞'],
            '爵士舞': ['爵士舞培训', '爵士舞教学', '爵士舞班', '爵士舞学校', '爵士舞教室', 'JAZZ舞蹈', '学爵士舞', '爵士舞蹈'],
            '街舞': ['街舞培训', '街舞教学', '街舞班', '街舞学校', '街舞教室', 'hiphop', '街舞工作室', '学街舞', '嘻哈舞', '韩舞'],
            '肚皮舞': ['肚皮舞培训', '肚皮舞教学', '肚皮舞班', '肚皮舞学校', '学肚皮舞'],
            
            # 美术绘画类
            '美术': ['美术培训', '绘画培训', '美术教学', '美术班', '美术学校', '美术中心', '画画培训', '美术教室', '少儿美术', '美术工作室', '美术课程', '画室'],
            '素描': ['素描培训', '素描教学', '素描班', '素描学校', '素描教室', '学素描', '素描课程', '素描工作室'],
            '国画': ['国画培训', '国画教学', '国画班', '国画学校', '国画教室', '学国画', '中国画培训', '水墨画培训'],
            '油画': ['油画培训', '油画教学', '油画班', '油画学校', '油画教室', '学油画', '油画工作室'],
            '水彩画': ['水彩画培训', '水彩培训', '水彩画教学', '水彩班', '学水彩', '水彩画教室'],
            '水粉画': ['水粉画培训', '水粉培训', '水粉画教学', '水粉班', '学水粉'],
            '彩铅画': ['彩铅培训', '彩铅画教学', '彩铅班', '彩色铅笔', '学彩铅'],
            '漫画': ['漫画培训', '漫画教学', '漫画班', '漫画学校', '学漫画', '动漫培训', '插画培训'],
            '速写': ['速写培训', '速写教学', '速写班', '学速写'],
            '儿童画': ['儿童画培训', '儿童画教学', '儿童画班', '创意美术', '幼儿美术'],
            
            # 书法类
            '书法': ['书法培训', '书法教学', '书法班', '书法学校', '书法教室', '书法中心', '书法艺术', '书法工作室', '书法课程'],
            '硬笔书法': ['硬笔书法培训', '硬笔书法教学', '硬笔书法班', '硬笔书法教室', '钢笔字培训', '硬笔练字'],
            '软笔书法': ['软笔书法培训', '软笔书法教学', '软笔书法班', '毛笔字培训', '毛笔书法', '学毛笔字'],
            
            # 语言表演类
            '口才': ['口才培训', '演讲培训', '主持培训', '口才教学', '口才班', '演讲口才', '小主持人', '语言表达', '播音主持', '口才艺术', '主持人培训', '少儿口才', '演讲与口才'],
            '播音主持': ['播音主持培训', '播音主持教学', '播音主持班', '主持人培训', '播音艺术', '主持培训'],
            '语言': ['语言培训', '语言艺术', '语言教学', '语言班', '语言表演', '语言中心', '语言课程', '小小主持人', '语言艺术培训'],
            '朗诵': ['朗诵培训', '朗诵教学', '朗诵班', '朗诵艺术', '朗诵中心', '诗歌朗诵', '配音朗诵', '学朗诵', '朗诵课程'],
            '相声': ['相声培训', '相声教学', '相声班', '学相声', '曲艺培训'],
            
            # 其他艺术类
            '表演': ['表演培训', '表演教学', '表演班', '表演艺术', '影视表演', '戏剧表演', '少儿表演'],
            '模特': ['模特培训', '模特班', '少儿模特', '模特艺术', 'T台走秀', '形体训练'],
            '摄影': ['摄影培训', '摄影教学', '摄影班', '摄影学校', '学摄影', '摄影艺术'],
            '陶艺': ['陶艺培训', '陶艺教学', '陶艺班', '陶艺工作室', '学陶艺', '陶瓷艺术'],
            '围棋': ['围棋培训', '围棋教学', '围棋班', '围棋学校', '学围棋', '围棋课程'],
            '象棋': ['象棋培训', '象棋教学', '象棋班', '象棋学校', '学象棋'],
            '跆拳道': ['跆拳道培训', '跆拳道教学', '跆拳道班', '跆拳道馆', '学跆拳道'],
            '武术': ['武术培训', '武术教学', '武术班', '武术学校', '学武术', '武术馆'],
        }
        
        # 自定义专业分类（用户自己添加的）
        self.custom_categories = {}
        
        self.create_widgets()
        self.load_config()
    
    def load_china_cities(self):
        """从JSON文件加载全国城市"""
        try:
            with open('china_cities.json', 'r', encoding='utf-8') as f:
                self.preset_cities = json.load(f)
        except:
            # 如果文件不存在，使用默认数据
            self.preset_cities = {
                '山东省': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '临沂市', '德州市', '聊城市', '滨州市', '菏泽市'],
            }
    
    def create_widgets(self):
        # 创建notebook（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本设置")
        
        city_frame = ttk.Frame(notebook, padding="10")
        notebook.add(city_frame, text="城市管理")
        
        category_frame = ttk.Frame(notebook, padding="10")
        notebook.add(category_frame, text="专业管理")
        
        self.setup_basic_tab(basic_frame)
        self.setup_city_tab(city_frame)
        self.setup_category_tab(category_frame)
    
    def setup_basic_tab(self, parent):
        # 创建左右两列布局
        left_column = ttk.Frame(parent)
        left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        right_column = ttk.Frame(parent)
        right_column.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # ========== 左列 ==========
        
        # API Key
        api_frame = ttk.LabelFrame(left_column, text="🔑 API Key配置", padding="10")
        api_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(api_frame, text="API Key:", font=("微软雅黑", 9)).pack(anchor=tk.W, pady=2)
        self.api_key_var = tk.StringVar(value="d127687049259dc6c806bae51df481c1")
        ttk.Entry(api_frame, textvariable=self.api_key_var, width=45, font=("Consolas", 9)).pack(fill=tk.X, pady=2)
        ttk.Label(api_frame, text="💡 购买流量包：30元/万次请求", foreground="gray", font=("微软雅黑", 8)).pack(anchor=tk.W)
        
        # 采集参数
        param_frame = ttk.LabelFrame(left_column, text="⚙️ 采集参数", padding="10")
        param_frame.pack(fill=tk.X, pady=10)
        
        # 搜索深度
        depth_frame = ttk.Frame(param_frame)
        depth_frame.pack(fill=tk.X, pady=5)
        ttk.Label(depth_frame, text="搜索深度(页):", width=15).pack(side=tk.LEFT)
        self.depth_var = tk.StringVar(value="30")
        ttk.Spinbox(depth_frame, from_=10, to=50, textvariable=self.depth_var, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Label(depth_frame, text="推荐: 20-30页", foreground="green", font=("微软雅黑", 8)).pack(side=tk.LEFT)
        
        # 请求延迟
        delay_frame = ttk.Frame(param_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        ttk.Label(delay_frame, text="请求延迟(秒):", width=15).pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="0.05")
        ttk.Spinbox(delay_frame, from_=0.01, to=1.0, increment=0.01, textvariable=self.delay_var, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Label(delay_frame, text="推荐: 0.05秒", foreground="green", font=("微软雅黑", 8)).pack(side=tk.LEFT)
        
        # 参数说明
        param_info = ttk.Frame(param_frame)
        param_info.pack(fill=tk.X, pady=5)
        ttk.Label(param_info, text="📊 预计API消耗：", font=("微软雅黑", 8, "bold")).pack(anchor=tk.W)
        self.api_cost_var = tk.StringVar(value="城市数 × 专业数 × 关键词数 × 深度 ≈ 0 次")
        ttk.Label(param_info, textvariable=self.api_cost_var, foreground="#666", font=("微软雅黑", 8)).pack(anchor=tk.W, padx=15)
        
        # 输出文件
        output_frame = ttk.LabelFrame(left_column, text="💾 输出设置", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="保存位置:", font=("微软雅黑", 9)).pack(anchor=tk.W, pady=2)
        file_frame = ttk.Frame(output_frame)
        file_frame.pack(fill=tk.X)
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Desktop', '采集数据.xlsx'))
        ttk.Entry(file_frame, textvariable=self.output_var, width=35, font=("微软雅黑", 8)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="浏览", command=self.browse_file, width=8).pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        control_frame = ttk.LabelFrame(left_column, text="🎮 控制面板", padding="10")
        control_frame.pack(fill=tk.X, pady=10)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="▶️ 开始采集", command=self.start_scraping, width=18)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹️ 停止采集", command=self.stop_scraping, width=18, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="💾 保存配置", command=self.save_config, width=12).pack(side=tk.LEFT, padx=5)
        
        # ========== 右列 ==========
        
        # 统计信息
        stat_frame = ttk.LabelFrame(right_column, text="📊 当前配置统计", padding="10")
        stat_frame.pack(fill=tk.X, pady=5)
        
        self.config_info_var = tk.StringVar(value="城市: 0个 | 专业: 0个 | 关键词: 0个")
        ttk.Label(stat_frame, textvariable=self.config_info_var, font=("微软雅黑", 11, "bold"), 
                 foreground="#0066cc").pack(pady=5)
        
        # 系统信息网格
        info_grid = ttk.Frame(stat_frame)
        info_grid.pack(fill=tk.X, pady=5)
        
        # 第一行
        ttk.Label(info_grid, text="📍 已加载省份:", font=("微软雅黑", 9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_grid, text=f"{len(self.preset_cities)}个", foreground="green", font=("微软雅黑", 9, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="🏙️ 可选城市:", font=("微软雅黑", 9)).grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        total_cities = sum(len(cities) for cities in self.preset_cities.values())
        ttk.Label(info_grid, text=f"{total_cities}个", foreground="green", font=("微软雅黑", 9, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # 第二行
        ttk.Label(info_grid, text="🎨 预设专业:", font=("微软雅黑", 9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_grid, text=f"{len(self.preset_keywords)}个", foreground="blue", font=("微软雅黑", 9, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="🔑 预设关键词:", font=("微软雅黑", 9)).grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        total_keywords = sum(len(kws) for kws in self.preset_keywords.values())
        ttk.Label(info_grid, text=f"{total_keywords}个", foreground="blue", font=("微软雅黑", 9, "bold")).grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # 详细配置信息 + 运行监控（Notebook切换）
        detail_frame = ttk.LabelFrame(right_column, text="📝 详细信息", padding="5")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建Notebook用于切换
        detail_notebook = ttk.Notebook(detail_frame)
        detail_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 配置信息标签页
        config_frame = ttk.Frame(detail_notebook)
        detail_notebook.add(config_frame, text="📋 配置详情")
        
        detail_text = tk.Text(config_frame, height=12, wrap=tk.WORD, font=("微软雅黑", 9), 
                             background="#f8f9fa", relief=tk.FLAT, padx=10, pady=10)
        detail_text.pack(fill=tk.BOTH, expand=True)
        
        detail_scrollbar = ttk.Scrollbar(detail_text, command=detail_text.yview)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text_widget = detail_text
        self.update_detail_info()
        detail_text.config(state=tk.DISABLED)
        
        # 运行监控标签页
        monitor_frame = ttk.Frame(detail_notebook)
        detail_notebook.add(monitor_frame, text="▶️ 运行监控")
        
        # 进度条
        progress_frame = ttk.Frame(monitor_frame)
        progress_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 状态文本
        self.progress_status_var = tk.StringVar(value="等待开始...")
        ttk.Label(progress_frame, textvariable=self.progress_status_var, 
                 font=("微软雅黑", 9), foreground="#0066cc").pack(anchor=tk.W, pady=2)
        
        # 进度条
        bar_frame = ttk.Frame(progress_frame)
        bar_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(bar_frame, text="进度:", font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bar_frame, variable=self.progress_var, 
                                           maximum=100, length=250)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label = ttk.Label(bar_frame, text="0%", font=("微软雅黑", 9, "bold"), 
                                       foreground="#00aa00", width=6)
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        self.stat_var = tk.StringVar(value="数据量: 0 条 | 过滤: 0 条 | 耗时: 0 秒")
        ttk.Label(progress_frame, textvariable=self.stat_var, 
                 font=("微软雅黑", 9, "bold"), foreground="#666").pack(anchor=tk.W, pady=2)
        
        # 日志显示
        log_frame = ttk.Frame(monitor_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, 
                               font=("Consolas", 9), yscrollcommand=log_scrollbar.set,
                               background="#1e1e1e", foreground="#ffffff")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.config(command=self.log_text.yview)
        
        # 配置标签颜色
        self.log_text.tag_config("INFO", foreground="#00ff00")
        self.log_text.tag_config("SUCCESS", foreground="#00ff00", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("ERROR", foreground="#ff0000", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("WARNING", foreground="#ffaa00")
        self.log_text.tag_config("HEADER", foreground="#00aaff", font=("Consolas", 9, "bold"))
        
        # 添加初始欢迎信息
        self.log_text.insert("1.0", "系统就绪，等待开始采集...\n", "INFO")
        self.log_text.config(state=tk.DISABLED)
        
        # 快捷操作
        quick_frame = ttk.LabelFrame(right_column, text="⚡ 快捷操作", padding="10")
        quick_frame.pack(fill=tk.X, pady=5)
        
        quick_btn_frame = ttk.Frame(quick_frame)
        quick_btn_frame.pack(fill=tk.X)
        
        ttk.Button(quick_btn_frame, text="💡 查看使用指南", command=self.show_guide, width=15).pack(side=tk.LEFT, padx=3)
        ttk.Button(quick_btn_frame, text="🌟 一键配置山东省", command=self.quick_config_shandong, width=16).pack(side=tk.LEFT, padx=3)
        ttk.Button(quick_btn_frame, text="🔥 热门专业推荐", command=self.show_hot_categories, width=15).pack(side=tk.LEFT, padx=3)
        
        
        # 配置行列权重
        parent.rowconfigure(5, weight=1)
    
    def update_detail_info(self):
        """更新详细配置信息"""
        if hasattr(self, 'detail_text_widget'):
            self.detail_text_widget.config(state=tk.NORMAL)
            self.detail_text_widget.delete("1.0", tk.END)
            
            # 获取当前配置
            selected_cities = list(self.city_listbox.get(0, tk.END)) if hasattr(self, 'city_listbox') else []
            selected_categories = list(self.category_listbox.get(0, tk.END)) if hasattr(self, 'category_listbox') else []
            
            # 计算关键词总数
            total_keywords = 0
            for cat in selected_categories:
                if cat in self.preset_keywords:
                    total_keywords += len(self.preset_keywords[cat])
                elif cat in self.custom_categories:
                    total_keywords += len(self.custom_categories[cat])
            
            # 更新标题统计
            self.config_info_var.set(f"城市: {len(selected_cities)}个 | 专业: {len(selected_categories)}个 | 关键词: {total_keywords}个")
            
            # 详细信息
            info_text = ""
            
            # 采集城市列表
            if selected_cities:
                info_text += "✅ 已选择城市：\n"
                for i, city in enumerate(selected_cities, 1):
                    if i <= 10:  # 最多显示10个
                        info_text += f"   {i}. {city}\n"
                if len(selected_cities) > 10:
                    info_text += f"   ... 还有 {len(selected_cities)-10} 个城市\n"
            else:
                info_text += "❌ 未选择城市\n"
            
            info_text += "\n"
            
            # 采集专业列表
            if selected_categories:
                info_text += "✅ 已选择专业：\n"
                for i, cat in enumerate(selected_categories, 1):
                    if cat in self.preset_keywords:
                        kw_count = len(self.preset_keywords[cat])
                    elif cat in self.custom_categories:
                        kw_count = len(self.custom_categories[cat])
                    else:
                        kw_count = 0
                    info_text += f"   {i}. {cat} ({kw_count}个关键词)\n"
            else:
                info_text += "❌ 未选择专业\n"
            
            info_text += "\n"
            
            # API消耗预估
            try:
                depth = int(self.depth_var.get())
            except:
                depth = 30
            
            estimated_calls = len(selected_cities) * len(selected_categories) * total_keywords * depth
            info_text += f"📊 预计API消耗：\n"
            info_text += f"   {len(selected_cities)}城市 × {len(selected_categories)}专业 × {total_keywords}关键词 × {depth}页\n"
            info_text += f"   ≈ {estimated_calls:,} 次请求\n\n"
            
            # 费用预估
            if estimated_calls > 0:
                cost = estimated_calls / 10000 * 30  # 30元/万次
                info_text += f"💰 预估费用：约 {cost:.2f} 元\n\n"
            
            # 操作提示
            info_text += "💡 提示：\n"
            info_text += "   • 到【城市管理】选择要采集的城市\n"
            info_text += "   • 到【专业管理】选择要采集的专业\n"
            info_text += "   • 配置好后点击【开始采集】按钮\n"
            info_text += "   • 采集过程可到【运行监控】查看\n"
            
            self.detail_text_widget.insert("1.0", info_text)
            self.detail_text_widget.config(state=tk.DISABLED)
            
            # 更新API消耗显示
            if hasattr(self, 'api_cost_var'):
                if estimated_calls > 0:
                    self.api_cost_var.set(f"{len(selected_cities)}城市 × {len(selected_categories)}专业 × {total_keywords}关键词 × {depth}页 ≈ {estimated_calls:,} 次")
                else:
                    self.api_cost_var.set("城市数 × 专业数 × 关键词数 × 深度 ≈ 0 次")
    
    def setup_city_tab(self, parent):
        # 左侧：预设城市
        left_frame = ttk.LabelFrame(parent, text="快速选择（全国城市）", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 省份选择
        ttk.Label(left_frame, text="选择省份/直辖市:").pack(anchor=tk.W, pady=5)
        province_frame = ttk.Frame(left_frame)
        province_frame.pack(fill=tk.X, pady=5)
        
        self.province_var = tk.StringVar(value=list(self.preset_cities.keys())[0] if self.preset_cities else "")
        province_combo = ttk.Combobox(province_frame, textvariable=self.province_var, 
                                     values=list(self.preset_cities.keys()), width=20)
        province_combo.pack(side=tk.LEFT, padx=5)
        province_combo.bind('<<ComboboxSelected>>', self.update_preset_cities)
        
        ttk.Button(province_frame, text="快速添加该省所有城市", 
                  command=self.add_province_cities).pack(side=tk.LEFT, padx=5)
        
        # 预设城市列表
        preset_list_frame = ttk.Frame(left_frame)
        preset_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        preset_scrollbar = ttk.Scrollbar(preset_list_frame)
        preset_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preset_city_listbox = tk.Listbox(preset_list_frame, selectmode=tk.MULTIPLE, 
                                              yscrollcommand=preset_scrollbar.set, height=15)
        self.preset_city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preset_scrollbar.config(command=self.preset_city_listbox.yview)
        
        ttk.Button(left_frame, text="添加选中城市 →", 
                  command=self.add_selected_preset_cities).pack(pady=5)
        
        # 右侧：自定义城市
        right_frame = ttk.LabelFrame(parent, text="自定义输入", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 手动输入
        input_frame = ttk.Frame(right_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="输入城市名:").pack(side=tk.LEFT, padx=5)
        self.city_input_var = tk.StringVar()
        city_entry = ttk.Entry(input_frame, textvariable=self.city_input_var, width=15)
        city_entry.pack(side=tk.LEFT, padx=5)
        city_entry.bind('<Return>', lambda e: self.add_custom_city())
        
        ttk.Button(input_frame, text="添加", command=self.add_custom_city).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(right_frame, text="提示：输入完整城市名，如\"北京市\"、\"上海市\"", 
                 foreground="gray").pack(anchor=tk.W, pady=2)
        
        # 已选城市列表
        ttk.Label(right_frame, text="已选城市列表:").pack(anchor=tk.W, pady=5)
        
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.city_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                       yscrollcommand=scrollbar.set, height=15)
        self.city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.city_listbox.yview)
        
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="删除选中", command=self.remove_selected_cities).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空全部", command=self.clear_all_cities).pack(side=tk.LEFT, padx=5)
        
        # 配置权重
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 初始化
        self.update_preset_cities()
    
    def setup_category_tab(self, parent):
        # 左侧：预设专业
        left_frame = ttk.LabelFrame(parent, text="快速选择（预设专业）", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(left_frame, text="点击添加预设专业:").pack(anchor=tk.W, pady=5)
        
        preset_list_frame = ttk.Frame(left_frame)
        preset_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        preset_scrollbar = ttk.Scrollbar(preset_list_frame)
        preset_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preset_category_listbox = tk.Listbox(preset_list_frame, selectmode=tk.MULTIPLE,
                                                  yscrollcommand=preset_scrollbar.set, height=20)
        self.preset_category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preset_scrollbar.config(command=self.preset_category_listbox.yview)
        
        for cat in self.preset_keywords.keys():
            self.preset_category_listbox.insert(tk.END, f"{cat} ({len(self.preset_keywords[cat])}个关键词)")
        
        btn_frame_left = ttk.Frame(left_frame)
        btn_frame_left.pack(pady=5)
        
        ttk.Button(btn_frame_left, text="查看关键词", 
                  command=self.view_keywords).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_left, text="编辑关键词", 
                  command=self.edit_preset_keywords).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_left, text="添加选中专业 →", 
                  command=self.add_selected_preset_categories).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(left_frame, text="添加全部预设专业 →", 
                  command=self.add_all_preset_categories).pack(pady=5)
        
        # 右侧：自定义专业
        right_frame = ttk.LabelFrame(parent, text="自定义专业", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 输入框
        input_frame = ttk.Frame(right_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="专业名称:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.category_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.category_name_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="搜索关键词:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_keywords_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.category_keywords_var, width=30).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(right_frame, text="提示：多个关键词用逗号分隔，如\"钢琴培训,钢琴教学,钢琴班\"", 
                 foreground="gray").pack(anchor=tk.W, pady=2)
        
        ttk.Button(right_frame, text="添加自定义专业", command=self.add_custom_category).pack(pady=5)
        
        # 已选专业列表
        ttk.Label(right_frame, text="已选专业列表:").pack(anchor=tk.W, pady=5)
        
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED,
                                          yscrollcommand=scrollbar.set, height=15)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.category_listbox.yview)
        
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="查看关键词", command=self.view_selected_keywords).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑关键词", command=self.edit_keywords).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.remove_selected_categories).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空全部", command=self.clear_all_categories).pack(side=tk.LEFT, padx=5)
        
        # 配置权重
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
    
    
    # ========== 城市管理方法 ==========
    
    def update_preset_cities(self, event=None):
        province = self.province_var.get()
        self.preset_city_listbox.delete(0, tk.END)
        if province in self.preset_cities:
            for city in self.preset_cities[province]:
                self.preset_city_listbox.insert(tk.END, city)
    
    def add_province_cities(self):
        province = self.province_var.get()
        if province in self.preset_cities:
            for city in self.preset_cities[province]:
                if city not in self.city_listbox.get(0, tk.END):
                    self.city_listbox.insert(tk.END, city)
            self.update_config_info()
            messagebox.showinfo("成功", f"已添加{province}的{len(self.preset_cities[province])}个城市")
    
    def add_selected_preset_cities(self):
        selected = self.preset_city_listbox.curselection()
        for idx in selected:
            city = self.preset_city_listbox.get(idx)
            if city not in self.city_listbox.get(0, tk.END):
                self.city_listbox.insert(tk.END, city)
        self.update_config_info()
    
    def add_custom_city(self):
        city = self.city_input_var.get().strip()
        if city:
            if not city.endswith('市'):
                city += '市'
            if city not in self.city_listbox.get(0, tk.END):
                self.city_listbox.insert(tk.END, city)
                self.city_input_var.set("")
                self.update_config_info()
            else:
                messagebox.showwarning("提示", "该城市已存在")
    
    def remove_selected_cities(self):
        selected = self.city_listbox.curselection()
        for idx in reversed(selected):
            self.city_listbox.delete(idx)
        self.update_config_info()
    
    def clear_all_cities(self):
        if messagebox.askyesno("确认", "确定要清空所有城市吗？"):
            self.city_listbox.delete(0, tk.END)
            self.update_config_info()
    
    # ========== 专业管理方法 ==========
    
    def add_selected_preset_categories(self):
        selected = self.preset_category_listbox.curselection()
        for idx in selected:
            cat_text = self.preset_category_listbox.get(idx)
            cat_name = cat_text.split(' (')[0]
            if cat_name not in [item.split(' (')[0] for item in self.category_listbox.get(0, tk.END)]:
                keywords_count = len(self.preset_keywords[cat_name])
                self.category_listbox.insert(tk.END, f"{cat_name} ({keywords_count}个关键词)")
        self.update_config_info()
    
    def add_all_preset_categories(self):
        for cat, keywords in self.preset_keywords.items():
            if cat not in [item.split(' (')[0] for item in self.category_listbox.get(0, tk.END)]:
                self.category_listbox.insert(tk.END, f"{cat} ({len(keywords)}个关键词)")
        self.update_config_info()
        messagebox.showinfo("成功", f"已添加所有{len(self.preset_keywords)}个预设专业")
    
    def edit_preset_keywords(self):
        """编辑预设专业的关键词"""
        selected = self.preset_category_listbox.curselection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个专业")
            return
        
        # 只编辑第一个选中的
        idx = selected[0]
        cat_text = self.preset_category_listbox.get(idx)
        cat_name = cat_text.split(' (')[0]
        
        # 获取当前关键词
        if cat_name in self.preset_keywords:
            current_keywords = self.preset_keywords[cat_name]
        else:
            current_keywords = []
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑关键词 - {cat_name}")
        edit_window.geometry("600x550")
        
        ttk.Label(edit_window, text=f"编辑【{cat_name}】的搜索关键词", 
                 font=("微软雅黑", 12, "bold")).pack(pady=10)
        
        ttk.Label(edit_window, text="当前关键词列表：", 
                 font=("微软雅黑", 10)).pack(anchor=tk.W, padx=20, pady=5)
        
        # 关键词列表框
        list_frame = ttk.Frame(edit_window, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        keyword_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED,
                                     yscrollcommand=scrollbar.set, height=15,
                                     font=("微软雅黑", 10))
        keyword_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=keyword_listbox.yview)
        
        # 填充当前关键词
        for kw in current_keywords:
            keyword_listbox.insert(tk.END, kw)
        
        # 添加/删除关键词的控制
        control_frame = ttk.Frame(edit_window, padding="10")
        control_frame.pack(fill=tk.X, padx=20)
        
        ttk.Label(control_frame, text="添加新关键词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        new_keyword_var = tk.StringVar()
        new_keyword_entry = ttk.Entry(control_frame, textvariable=new_keyword_var, width=30)
        new_keyword_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def add_keyword():
            kw = new_keyword_var.get().strip()
            if kw:
                if kw not in keyword_listbox.get(0, tk.END):
                    keyword_listbox.insert(tk.END, kw)
                    new_keyword_var.set("")
                else:
                    messagebox.showwarning("提示", "该关键词已存在")
        
        ttk.Button(control_frame, text="添加", command=add_keyword).grid(row=0, column=2, padx=5)
        new_keyword_entry.bind('<Return>', lambda e: add_keyword())
        
        def delete_selected():
            selected = keyword_listbox.curselection()
            for i in reversed(selected):
                keyword_listbox.delete(i)
        
        ttk.Button(control_frame, text="删除选中关键词", 
                  command=delete_selected).grid(row=1, column=0, columnspan=3, pady=10)
        
        # 保存和取消按钮
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(pady=10)
        
        def save_changes():
            # 获取所有关键词
            keywords = list(keyword_listbox.get(0, tk.END))
            
            if not keywords:
                messagebox.showwarning("提示", "至少需要一个关键词")
                return
            
            # 更新关键词库
            self.preset_keywords[cat_name] = keywords
            
            # 更新预设列表显示
            self.preset_category_listbox.delete(idx)
            self.preset_category_listbox.insert(idx, f"{cat_name} ({len(keywords)}个关键词)")
            self.preset_category_listbox.selection_set(idx)
            
            # 如果该专业在已选列表中，也更新
            for i in range(self.category_listbox.size()):
                item_text = self.category_listbox.get(i)
                item_name = item_text.split(' (')[0]
                if item_name == cat_name:
                    self.category_listbox.delete(i)
                    self.category_listbox.insert(i, f"{cat_name} ({len(keywords)}个关键词)")
                    break
            
            self.update_config_info()
            messagebox.showinfo("成功", f"已更新【{cat_name}】的关键词，共{len(keywords)}个")
            edit_window.destroy()
        
        ttk.Button(btn_frame, text="保存修改", command=save_changes, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=edit_window.destroy, width=15).pack(side=tk.LEFT, padx=10)
        
        # 提示信息
        ttk.Label(edit_window, text="提示：可以添加、删除关键词，修改后点击'保存修改'", 
                 foreground="gray").pack(pady=5)
    
    def view_keywords(self):
        """查看预设专业的关键词"""
        selected = self.preset_category_listbox.curselection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个专业")
            return
        
        # 只查看第一个选中的
        idx = selected[0]
        cat_text = self.preset_category_listbox.get(idx)
        cat_name = cat_text.split(' (')[0]
        
        if cat_name in self.preset_keywords:
            keywords = self.preset_keywords[cat_name]
            keywords_str = '\n'.join([f"{i+1}. {kw}" for i, kw in enumerate(keywords)])
            
            # 创建新窗口显示
            view_window = tk.Toplevel(self.root)
            view_window.title(f"{cat_name} - 搜索关键词")
            view_window.geometry("400x500")
            
            ttk.Label(view_window, text=f"【{cat_name}】专业的搜索关键词：", 
                     font=("微软雅黑", 11, "bold")).pack(pady=10)
            ttk.Label(view_window, text=f"共{len(keywords)}个关键词", 
                     foreground="blue").pack()
            
            text_frame = ttk.Frame(view_window, padding="10")
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                          wrap=tk.WORD, font=("微软雅黑", 10))
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text.yview)
            
            text.insert(tk.END, keywords_str)
            text.config(state=tk.DISABLED)
            
            ttk.Button(view_window, text="关闭", 
                      command=view_window.destroy).pack(pady=10)
    
    def view_selected_keywords(self):
        """查看已选专业的关键词"""
        selected = self.category_listbox.curselection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个专业")
            return
        
        # 只查看第一个选中的
        idx = selected[0]
        cat_text = self.category_listbox.get(idx)
        cat_name = cat_text.split(' (')[0]
        
        if cat_name in self.preset_keywords:
            keywords = self.preset_keywords[cat_name]
            keywords_str = '\n'.join([f"{i+1}. {kw}" for i, kw in enumerate(keywords)])
            
            # 创建新窗口显示
            view_window = tk.Toplevel(self.root)
            view_window.title(f"{cat_name} - 搜索关键词")
            view_window.geometry("400x500")
            
            ttk.Label(view_window, text=f"【{cat_name}】专业的搜索关键词：", 
                     font=("微软雅黑", 11, "bold")).pack(pady=10)
            ttk.Label(view_window, text=f"共{len(keywords)}个关键词", 
                     foreground="blue").pack()
            
            text_frame = ttk.Frame(view_window, padding="10")
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                          wrap=tk.WORD, font=("微软雅黑", 10))
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text.yview)
            
            text.insert(tk.END, keywords_str)
            text.config(state=tk.DISABLED)
            
            ttk.Button(view_window, text="关闭", 
                      command=view_window.destroy).pack(pady=10)
        else:
            messagebox.showinfo("提示", f"专业【{cat_name}】没有预设关键词")
    
    def edit_keywords(self):
        """编辑专业的关键词"""
        selected = self.category_listbox.curselection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个专业")
            return
        
        # 只编辑第一个选中的
        idx = selected[0]
        cat_text = self.category_listbox.get(idx)
        cat_name = cat_text.split(' (')[0]
        
        # 获取当前关键词
        if cat_name in self.preset_keywords:
            current_keywords = self.preset_keywords[cat_name]
        else:
            current_keywords = []
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑关键词 - {cat_name}")
        edit_window.geometry("600x550")
        
        ttk.Label(edit_window, text=f"编辑【{cat_name}】的搜索关键词", 
                 font=("微软雅黑", 12, "bold")).pack(pady=10)
        
        ttk.Label(edit_window, text="当前关键词列表：", 
                 font=("微软雅黑", 10)).pack(anchor=tk.W, padx=20, pady=5)
        
        # 关键词列表框
        list_frame = ttk.Frame(edit_window, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        keyword_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED,
                                     yscrollcommand=scrollbar.set, height=15,
                                     font=("微软雅黑", 10))
        keyword_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=keyword_listbox.yview)
        
        # 填充当前关键词
        for kw in current_keywords:
            keyword_listbox.insert(tk.END, kw)
        
        # 添加/删除关键词的控制
        control_frame = ttk.Frame(edit_window, padding="10")
        control_frame.pack(fill=tk.X, padx=20)
        
        ttk.Label(control_frame, text="添加新关键词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        new_keyword_var = tk.StringVar()
        new_keyword_entry = ttk.Entry(control_frame, textvariable=new_keyword_var, width=30)
        new_keyword_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def add_keyword():
            kw = new_keyword_var.get().strip()
            if kw:
                if kw not in keyword_listbox.get(0, tk.END):
                    keyword_listbox.insert(tk.END, kw)
                    new_keyword_var.set("")
                else:
                    messagebox.showwarning("提示", "该关键词已存在")
        
        ttk.Button(control_frame, text="添加", command=add_keyword).grid(row=0, column=2, padx=5)
        new_keyword_entry.bind('<Return>', lambda e: add_keyword())
        
        def delete_selected():
            selected = keyword_listbox.curselection()
            for i in reversed(selected):
                keyword_listbox.delete(i)
        
        ttk.Button(control_frame, text="删除选中关键词", 
                  command=delete_selected).grid(row=1, column=0, columnspan=3, pady=10)
        
        # 保存和取消按钮
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(pady=10)
        
        def save_changes():
            # 获取所有关键词
            keywords = list(keyword_listbox.get(0, tk.END))
            
            if not keywords:
                messagebox.showwarning("提示", "至少需要一个关键词")
                return
            
            # 更新关键词库
            self.preset_keywords[cat_name] = keywords
            
            # 更新列表显示
            self.category_listbox.delete(idx)
            self.category_listbox.insert(idx, f"{cat_name} ({len(keywords)}个关键词)")
            self.category_listbox.selection_set(idx)
            
            self.update_config_info()
            messagebox.showinfo("成功", f"已更新【{cat_name}】的关键词，共{len(keywords)}个")
            edit_window.destroy()
        
        ttk.Button(btn_frame, text="保存修改", command=save_changes, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=edit_window.destroy, width=15).pack(side=tk.LEFT, padx=10)
        
        # 提示信息
        ttk.Label(edit_window, text="提示：可以添加、删除关键词，修改后点击'保存修改'", 
                 foreground="gray").pack(pady=5)
    
    def add_custom_category(self):
        name = self.category_name_var.get().strip()
        keywords_str = self.category_keywords_var.get().strip()
        
        if not name or not keywords_str:
            messagebox.showwarning("提示", "请输入专业名称和关键词")
            return
        
        keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        if not keywords:
            messagebox.showwarning("提示", "请输入至少一个关键词")
            return
        
        # 添加到预设关键词库
        self.preset_keywords[name] = keywords
        
        # 添加到列表
        if name not in [item.split(' (')[0] for item in self.category_listbox.get(0, tk.END)]:
            self.category_listbox.insert(tk.END, f"{name} ({len(keywords)}个关键词)")
            self.category_name_var.set("")
            self.category_keywords_var.set("")
            self.update_config_info()
        else:
            messagebox.showwarning("提示", "该专业已存在")
    
    def remove_selected_categories(self):
        selected = self.category_listbox.curselection()
        for idx in reversed(selected):
            self.category_listbox.delete(idx)
        self.update_config_info()
    
    def clear_all_categories(self):
        if messagebox.askyesno("确认", "确定要清空所有专业吗？"):
            self.category_listbox.delete(0, tk.END)
            self.update_config_info()
    
    # ========== 配置管理 ==========
    
    def update_config_info(self):
        city_count = self.city_listbox.size()
        category_count = self.category_listbox.size()
        
        total_keywords = 0
        for item in self.category_listbox.get(0, tk.END):
            cat_name = item.split(' (')[0]
            if cat_name in self.preset_keywords:
                total_keywords += len(self.preset_keywords[cat_name])
        
        self.config_info_var.set(f"城市: {city_count}个 | 专业: {category_count}个 | 关键词: {total_keywords}个")
        
        # 更新详细配置信息
        self.update_detail_info()
    
    def save_config(self):
        config = {
            'api_key': self.api_key_var.get(),
            'cities': list(self.city_listbox.get(0, tk.END)),
            'categories': list(self.category_listbox.get(0, tk.END)),
            'depth': self.depth_var.get(),
            'delay': self.delay_var.get(),
            'output': self.output_var.get(),
            'custom_keywords': {k: v for k, v in self.preset_keywords.items() 
                              if k not in ['声乐', '器乐', '口才', '吉他', '古筝', '二胡', '舞蹈', 
                                          '语言', '朗诵', '拉丁舞', '民族舞', '现代舞', '美术', '书法']}
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{e}")
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.api_key_var.set(config.get('api_key', ''))
                self.depth_var.set(config.get('depth', '30'))
                self.delay_var.set(config.get('delay', '0.05'))
                self.output_var.set(config.get('output', ''))
                
                # 加载城市
                for city in config.get('cities', []):
                    self.city_listbox.insert(tk.END, city)
                
                # 加载专业
                for cat in config.get('categories', []):
                    self.category_listbox.insert(tk.END, cat)
                
                # 加载自定义关键词
                custom_kw = config.get('custom_keywords', {})
                self.preset_keywords.update(custom_kw)
                
                self.update_config_info()
            except Exception as e:
                pass
    
    def browse_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.output_var.set(filename)
    
    # ========== 快捷操作方法 ==========
    
    def show_guide(self):
        """显示使用指南"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("使用指南")
        guide_window.geometry("700x600")
        
        ttk.Label(guide_window, text="📖 全国艺术培训机构数据采集系统 - 使用指南", 
                 font=("微软雅黑", 13, "bold")).pack(pady=15)
        
        text_frame = ttk.Frame(guide_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD, 
                      font=("微软雅黑", 10), relief=tk.FLAT, bg="#f9f9f9")
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        guide_content = """
【快速开始】

第一步：选择城市
    • 进入【城市管理】标签页
    • 方式1：选择省份 → 点击"快速添加该省所有城市"
    • 方式2：手动输入城市名称（如：北京市、上海市）
    
第二步：选择专业
    • 进入【专业管理】标签页
    • 从左侧预设专业列表选择
    • 点击"添加选中专业 →"
    • 或点击"添加全部预设专业 →"
    
第三步：配置参数
    • 回到【基本设置】标签页
    • 确认API Key正确
    • 调整搜索深度（建议20-30页）
    • 设置请求延迟（建议0.05秒）
    
第四步：开始采集
    • 点击"开始采集"按钮
    • 切换到【运行监控】查看进度
    • 数据实时保存到桌面Excel文件
    
【高级功能】

• 查看关键词：点击"查看关键词"查看专业的搜索词
• 编辑关键词：点击"编辑关键词"自定义搜索词
• 自定义专业：输入专业名称和关键词添加新专业
• 保存配置：点击"保存配置"下次启动自动加载
    
【参数说明】

搜索深度（10-50页）：
    • 数值越大，采集数据越多
    • 但耗时也越长，API消耗越多
    • 推荐：20-30页平衡效率和数量
    
请求延迟（0.01-1.0秒）：
    • 每次API请求的间隔时间
    • 太快可能被限制，太慢效率低
    • 推荐：0.05秒（每秒20次请求）
    
【数据说明】

• 只保留：11位手机号（1开头的移动电话）
• 自动过滤：座机号码、无效号码
• 自动去重：相同机构+手机号组合
• 实时保存：每完成一个城市立即写入Excel
    
【注意事项】

1. API配额：免费版每天5000-6000次请求
2. 购买流量包：30元/万次，可采集更多数据
3. 网络稳定：确保网络连接良好
4. 耐心等待：全量采集需要10-20分钟
5. 随时中断：可以随时停止，已采集数据已保存
    
【常见问题】

Q: 为什么采集的数据比预期少？
A: 可能原因：API配额不足、搜索深度不够、该地区机构确实较少

Q: 如何获取更多数据？
A: 增加搜索深度、购买API流量包、添加更多搜索关键词

Q: 可以采集其他类型机构吗？
A: 可以！在【专业管理】添加自定义专业和关键词即可

Q: 数据准确性如何？
A: 数据来自高德地图公开数据，建议人工核验重要信息
        """
        
        text.insert(tk.END, guide_content)
        text.config(state=tk.DISABLED)
        
        ttk.Button(guide_window, text="关闭", command=guide_window.destroy, width=15).pack(pady=10)
    
    def quick_config_shandong(self):
        """一键配置山东省"""
        if messagebox.askyesno("确认", "是否一键配置山东省采集？\n\n将会：\n• 添加山东省16个城市\n• 添加14个热门专业"):
            # 清空现有配置
            self.city_listbox.delete(0, tk.END)
            self.category_listbox.delete(0, tk.END)
            
            # 添加山东省所有城市
            if '山东省' in self.preset_cities:
                for city in self.preset_cities['山东省']:
                    self.city_listbox.insert(tk.END, city)
            
            # 添加热门专业
            hot_cats = ['声乐', '舞蹈', '美术', '钢琴', '吉他', '古筝', '书法', 
                       '拉丁舞', '街舞', '口才', '播音主持', '跆拳道', '围棋', '象棋']
            for cat in hot_cats:
                if cat in self.preset_keywords:
                    self.category_listbox.insert(tk.END, f"{cat} ({len(self.preset_keywords[cat])}个关键词)")
            
            self.update_config_info()
            messagebox.showinfo("成功", f"已配置完成！\n\n城市：山东省16市\n专业：{len(hot_cats)}个\n\n可以直接开始采集了！")
    
    def show_hot_categories(self):
        """显示热门专业推荐"""
        hot_window = tk.Toplevel(self.root)
        hot_window.title("热门专业推荐")
        hot_window.geometry("600x500")
        
        ttk.Label(hot_window, text="🔥 热门专业推荐", 
                 font=("微软雅黑", 13, "bold")).pack(pady=15)
        
        text_frame = ttk.Frame(hot_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD, 
                      font=("微软雅黑", 10), relief=tk.FLAT, bg="#f9f9f9")
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        hot_content = """
【乐器类 - 最热门】
• 钢琴 - 最受欢迎的西洋乐器
• 吉他 - 民谣、电吉他、古典吉他
• 古筝 - 最受欢迎的民族乐器
• 架子鼓 - 打击乐器首选
• 小提琴 - 经典弦乐器

【舞蹈类 - 机构最多】
• 舞蹈（综合）- 覆盖面最广
• 拉丁舞 - 体育舞蹈、国标舞
• 街舞 - 年轻人最爱
• 芭蕾舞 - 形体气质培养
• 中国舞/民族舞 - 传统舞蹈

【美术类 - 机构密集】
• 美术（综合）- 少儿美术最多
• 素描 - 美术基础
• 国画 - 传统艺术
• 儿童画 - 少儿启蒙
• 书法 - 软笔、硬笔

【语言表演类 - 新兴热门】
• 口才 - 演讲与口才
• 播音主持 - 小主持人
• 表演 - 影视表演、戏剧
• 模特 - 少儿模特、T台

【体育艺术类 - 综合培养】
• 跆拳道 - 体能训练
• 武术 - 传统功夫
• 围棋 - 智力开发
• 象棋 - 思维训练

【推荐组合】

套餐1：音乐全科
→ 钢琴 + 小提琴 + 吉他 + 声乐

套餐2：舞蹈系列  
→ 舞蹈 + 拉丁舞 + 街舞 + 芭蕾舞

套餐3：美术书法
→ 美术 + 素描 + 国画 + 书法

套餐4：综合艺术
→ 钢琴 + 舞蹈 + 美术 + 口才 + 跆拳道

【采集建议】

• 针对性采集：只选1-3个专业，数据更精准
• 全面采集：选择所有专业，覆盖面更广
• 分批采集：每天采集不同专业，避免API限制
        """
        
        text.insert(tk.END, hot_content)
        text.config(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(hot_window)
        btn_frame.pack(pady=10)
        
        def add_hot():
            hot_window.destroy()
            self.quick_config_shandong()
        
        ttk.Button(btn_frame, text="一键添加热门专业", command=add_hot, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="关闭", command=hot_window.destroy, width=15).pack(side=tk.LEFT, padx=10)
    
    def log(self, message, tag="INFO"):
        """记录日志到运行监控窗口"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    # ========== 采集控制 ==========
    
    def start_scraping(self):
        # 验证
        if not self.api_key_var.get().strip():
            messagebox.showerror("错误", "请输入API Key")
            return
        
        if self.city_listbox.size() == 0:
            messagebox.showerror("错误", "请至少添加一个城市")
            return
        
        if self.category_listbox.size() == 0:
            messagebox.showerror("错误", "请至少添加一个专业")
            return
        
        # 获取配置
        cities = list(self.city_listbox.get(0, tk.END))
        categories_text = list(self.category_listbox.get(0, tk.END))
        categories = {}
        for cat_text in categories_text:
            cat_name = cat_text.split(' (')[0]
            if cat_name in self.preset_keywords:
                categories[cat_name] = self.preset_keywords[cat_name]
        
        # 禁用按钮
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_running = True
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 启动线程
        thread = threading.Thread(target=self.run_scraping, args=(cities, categories))
        thread.daemon = True
        thread.start()
    
    def stop_scraping(self):
        self.is_running = False
        self.log("\n⏸️ 用户手动停止采集...", "WARNING")
        self.stop_btn.config(state=tk.DISABLED)
    
    def run_scraping(self, cities, categories):
        try:
            start_time = time.time()
            
            # 创建采集器
            scraper = ShandongTrainingScraper(self.api_key_var.get())
            scraper.cities = cities
            scraper.categories = categories
            
            # 初始化Excel
            output_file = self.output_var.get()
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    output_file = output_file.replace('.xlsx', f'_{int(time.time())}.xlsx')
            
            wb = Workbook()
            ws = wb.active
            ws.title = "汇总"
            ws.append(['城市', '专业', '机构名称', '手机号'])
            wb.save(output_file)
            
            self.log(f"输出文件: {output_file}", "HEADER")
            self.log(f"城市: {len(cities)}个 | 专业: {len(categories)}个", "HEADER")
            self.log("="*60, "HEADER")
            
            # 采集
            total_collected = 0
            total_filtered = 0
            search_depth = int(self.depth_var.get())
            delay = float(self.delay_var.get())
            
            for city_idx, city in enumerate(cities, 1):
                if not self.is_running:
                    break
                
                # 更新进度
                progress_percent = (city_idx - 1) / len(cities) * 100
                self.progress_var.set(progress_percent)
                self.progress_label.config(text=f"{progress_percent:.1f}%")
                self.progress_status_var.set(f"正在采集: {city} ({city_idx}/{len(cities)})")
                self.root.update()
                
                self.log(f"\n{'='*50}", "HEADER")
                self.log(f"[{city}] 开始采集...", "HEADER")
                city_data = []
                
                for cat_idx, (category, keywords) in enumerate(categories.items(), 1):
                    if not self.is_running:
                        break
                    
                    self.log(f"  [{cat_idx}/{len(categories)}] {category}...", "INFO")
                    
                    for keyword in keywords:
                        if not self.is_running:
                            break
                        
                        page = 1
                        while page <= search_depth:
                            result = scraper.search_poi(city, keyword, page)
                            
                            if result and result.get('status') == '1':
                                pois = result.get('pois', [])
                                if not pois:
                                    break
                                
                                for poi in pois:
                                    name = poi.get('name', '')
                                    tel = poi.get('tel', '')
                                    district = poi.get('adname', '')
                                    cityname = poi.get('cityname', '')
                                    phones = scraper.extract_phone(tel)
                                    
                                    if phones:
                                        for phone in phones:
                                            city_data.append({
                                                '城市': f"{cityname}{district}" if district else cityname,
                                                '专业': category,
                                                '机构名称': name,
                                                '手机号': phone
                                            })
                                    else:
                                        total_filtered += 1
                                
                                page += 1
                                time.sleep(delay)
                            else:
                                break
                
                # 去重保存
                city_data = scraper.remove_duplicates(city_data)
                self.log(f"[{city}] 完成: {len(city_data)}条")
                
                if city_data:
                    df = pd.DataFrame(city_data)
                    df = df.sort_values(['专业', '机构名称'])
                    
                    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        try:
                            summary = pd.read_excel(output_file, sheet_name='汇总')
                            summary = pd.concat([summary, df], ignore_index=True)
                        except:
                            summary = df
                        summary.to_excel(writer, sheet_name='汇总', index=False)
                        
                        sheet_name = city.replace('市', '').replace('自治州', '').replace('特别行政区', '')[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    total_collected += len(city_data)
                    self.log(f"  ✓ 已保存 {len(city_data)}条 | 累计: {total_collected}条", "SUCCESS")
                
                elapsed = int(time.time() - start_time)
                self.stat_var.set(f"数据量: {total_collected} 条 | 过滤: {total_filtered} 条 | 耗时: {elapsed} 秒")
            
            # 完成
            self.progress_var.set(100)
            self.progress_label.config(text="100%")
            self.progress_status_var.set("采集完成！")
            
            elapsed = int(time.time() - start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            
            self.log("\n" + "="*60, "HEADER")
            self.log(f"🎉 采集完成！", "SUCCESS")
            self.log(f"✓ 有效数据: {total_collected}条", "SUCCESS")
            self.log(f"✗ 过滤数据: {total_filtered}条", "WARNING")
            self.log(f"⏱ 总耗时: {minutes}分{seconds}秒", "INFO")
            self.log(f"📁 保存位置: {output_file}", "INFO")
            self.log("="*60, "HEADER")
            
            messagebox.showinfo("完成", f"采集完成！\n共{total_collected}条数据\n耗时{minutes}分{seconds}秒")
            
        except Exception as e:
            self.log(f"\n❌ 错误: {str(e)}", "ERROR")
            messagebox.showerror("错误", f"采集出错：{str(e)}")
        
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = ChinaScraperGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

