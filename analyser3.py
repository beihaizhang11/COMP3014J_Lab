#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyser3.py - TCP Performance Analyzer
Analyzes performance of different TCP variants and queue algorithms

Features:
- Part A: Analyze 4 TCP variants (Reno, Cubic, Vegas, Yeah)
- Part B: Compare DropTail vs RED queue algorithms
- Part C: Reproducibility test
"""

import matplotlib
# Use non-interactive backend to avoid display issues
matplotlib.use('Agg')
# Disable warnings about fonts
import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import numpy as np
import csv
import os
from math import ceil

# Set matplotlib to use only ASCII characters
plt.rcParams['axes.unicode_minus'] = False

class TCPAnalyzer:
    """TCP trace文件分析器"""
    
    def __init__(self, trace_file, variant_name):
        """
        初始化分析器
        
        参数:
            trace_file: trace文件路径
            variant_name: TCP变体名称
        """
        self.trace_file = trace_file
        self.variant_name = variant_name
        self.flow1_data = {}  # flow id 1的数据 (source1, fid 1)
        self.flow2_data = {}  # flow id 2的数据 (source2, fid 2)
        
        # 初始化数据结构
        self._init_data_structures()
        
    def _init_data_structures(self):
        """初始化数据结构"""
        self.flow1_data = {
            'sent_packets': 0,
            'rcvd_packets': 0,
            'dropped_packets': 0,
            'total_bytes': 0,
            'throughput_samples': [],
            'timestamps': []
        }
        self.flow2_data = {
            'sent_packets': 0,
            'rcvd_packets': 0,
            'dropped_packets': 0,
            'total_bytes': 0,
            'throughput_samples': [],
            'timestamps': []
        }
        
    def parse_trace(self):
        """解析trace文件"""
        if not os.path.exists(self.trace_file):
            print(f"警告: 文件 {self.trace_file} 不存在")
            return
            
        flow1_bytes_per_second = {}
        flow2_bytes_per_second = {}
        
        with open(self.trace_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 12:
                    continue
                    
                event = parts[0]
                time = float(parts[1])
                packet_type = parts[4]
                packet_size = int(parts[5])
                
                # 获取flow id (在倒数第4个位置)
                if len(parts) >= 11:
                    flow_id = parts[-4].split('.')[0]
                else:
                    continue
                
                # 只处理TCP数据包
                if packet_type != 'tcp':
                    continue
                
                time_bucket = int(time)
                
                # 根据flow id分类
                if flow_id == '0':  # flow 1
                    if event == '+':  # 发送
                        self.flow1_data['sent_packets'] += 1
                    elif event == 'r':  # 接收
                        self.flow1_data['rcvd_packets'] += 1
                        self.flow1_data['total_bytes'] += packet_size
                        if time_bucket not in flow1_bytes_per_second:
                            flow1_bytes_per_second[time_bucket] = 0
                        flow1_bytes_per_second[time_bucket] += packet_size
                    elif event == 'd':  # 丢包
                        self.flow1_data['dropped_packets'] += 1
                        
                elif flow_id == '1':  # flow 2
                    if event == '+':
                        self.flow2_data['sent_packets'] += 1
                    elif event == 'r':
                        self.flow2_data['rcvd_packets'] += 1
                        self.flow2_data['total_bytes'] += packet_size
                        if time_bucket not in flow2_bytes_per_second:
                            flow2_bytes_per_second[time_bucket] = 0
                        flow2_bytes_per_second[time_bucket] += packet_size
                    elif event == 'd':
                        self.flow2_data['dropped_packets'] += 1
        
        # 转换为吞吐量时间序列
        if flow1_bytes_per_second:
            max_time = max(flow1_bytes_per_second.keys())
            for t in range(max_time + 1):
                bytes_val = flow1_bytes_per_second.get(t, 0)
                mbps = (bytes_val * 8) / 1e6  # 转换为Mbps
                self.flow1_data['throughput_samples'].append(mbps)
                self.flow1_data['timestamps'].append(t)
                
        if flow2_bytes_per_second:
            max_time = max(flow2_bytes_per_second.keys())
            for t in range(max_time + 1):
                bytes_val = flow2_bytes_per_second.get(t, 0)
                mbps = (bytes_val * 8) / 1e6
                self.flow2_data['throughput_samples'].append(mbps)
                self.flow2_data['timestamps'].append(t)
    
    def get_total_goodput(self):
        """计算总吞吐量 (Mbps)"""
        sim_time = 100.0  # 仿真时间100秒
        flow1_mbps = 0
        flow2_mbps = 0
        
        if sim_time > 0:
            flow1_mbps = (self.flow1_data['total_bytes'] * 8) / (sim_time * 1e6)
            flow2_mbps = (self.flow2_data['total_bytes'] * 8) / (sim_time * 1e6)
        
        return flow1_mbps + flow2_mbps
    
    def get_plr(self):
        """计算包丢失率 (%)"""
        flow1_total = self.flow1_data['sent_packets']
        flow2_total = self.flow2_data['sent_packets']
        flow1_dropped = self.flow1_data['dropped_packets']
        flow2_dropped = self.flow2_data['dropped_packets']
        
        total_sent = flow1_total + flow2_total
        total_dropped = flow1_dropped + flow2_dropped
        
        if total_sent > 0:
            plr = (total_dropped / total_sent) * 100
        else:
            plr = 0
            
        return plr
    
    def get_fairness_index(self, start_fraction=2/3):
        """
        计算Jain公平性指数
        
        参数:
            start_fraction: 从哪个时间点开始计算 (默认最后1/3)
        """
        # 获取最后1/3的吞吐量数据
        flow1_samples = self.flow1_data['throughput_samples']
        flow2_samples = self.flow2_data['throughput_samples']
        
        if not flow1_samples or not flow2_samples:
            return 0
        
        start_idx1 = int(len(flow1_samples) * start_fraction)
        start_idx2 = int(len(flow2_samples) * start_fraction)
        
        flow1_last_third = flow1_samples[start_idx1:]
        flow2_last_third = flow2_samples[start_idx2:]
        
        if not flow1_last_third or not flow2_last_third:
            return 0
        
        # 计算平均吞吐量
        avg_flow1 = np.mean(flow1_last_third)
        avg_flow2 = np.mean(flow2_last_third)
        
        # Jain's fairness index: (sum xi)^2 / (n * sum xi^2)
        x = [avg_flow1, avg_flow2]
        n = len(x)
        sum_x = sum(x)
        sum_x2 = sum(xi**2 for xi in x)
        
        if sum_x2 > 0:
            fairness = (sum_x ** 2) / (n * sum_x2)
        else:
            fairness = 0
            
        return fairness
    
    def get_stability_cov(self, start_fraction=2/3):
        """
        计算稳定性 (变异系数 CoV)
        
        参数:
            start_fraction: 从哪个时间点开始计算
        """
        # 合并两个flow的吞吐量
        flow1_samples = self.flow1_data['throughput_samples']
        flow2_samples = self.flow2_data['throughput_samples']
        
        if not flow1_samples and not flow2_samples:
            return float('inf')
        
        # 取最后1/3
        start_idx1 = int(len(flow1_samples) * start_fraction) if flow1_samples else 0
        start_idx2 = int(len(flow2_samples) * start_fraction) if flow2_samples else 0
        
        samples1 = flow1_samples[start_idx1:] if flow1_samples else []
        samples2 = flow2_samples[start_idx2:] if flow2_samples else []
        
        all_samples = samples1 + samples2
        
        if not all_samples:
            return float('inf')
        
        mean_val = np.mean(all_samples)
        std_val = np.std(all_samples)
        
        if mean_val > 0:
            cov = std_val / mean_val
        else:
            cov = float('inf')
            
        return cov


def run_part_a():
    """
    Part A: 分析四种TCP变体的性能
    """
    print("=" * 60)
    print("Part A: TCP变体分析 (DropTail)")
    print("=" * 60)
    
    variants = ['reno', 'cubic', 'vegas', 'yeah']
    results = {}
    analyzers = {}
    
    # 1. 解析所有trace文件
    for variant in variants:
        # 尝试两种可能的路径
        trace_file = f'comp3014j/{variant}Trace.tr'
        if not os.path.exists(trace_file):
            trace_file = f'{variant}Trace.tr'
        
        print(f"\n处理 {variant.upper()}...")
        analyzer = TCPAnalyzer(trace_file, variant)
        analyzer.parse_trace()
        analyzers[variant] = analyzer
        
        goodput = analyzer.get_total_goodput()
        plr = analyzer.get_plr()
        fairness = analyzer.get_fairness_index()
        cov = analyzer.get_stability_cov()
        
        results[variant] = {
            'goodput': goodput,
            'plr': plr,
            'fairness': fairness,
            'cov': cov
        }
        
        print(f"  吞吐量: {goodput:.2f} Mbps")
        print(f"  PLR: {plr:.4f}%")
        print(f"  公平性: {fairness:.4f}")
        print(f"  稳定性(CoV): {cov:.4f}")
    
    # 2. 打印表格
    print("\n表格 1: 每个流的总吞吐量和包丢失率")
    print("-" * 60)
    print(f"{'变体':<10} {'吞吐量 (Mbps)':<20} {'PLR (%)':<15}")
    print("-" * 60)
    for variant in variants:
        goodput = results[variant]['goodput']
        plr = results[variant]['plr']
        print(f"{variant:<10} {goodput:<20.2f} {plr:<15.4f}")
    print("-" * 60)
    
    # 保存到CSV
    csv_path = 'partA_goodput_plr.csv'
    if os.path.exists('comp3014j'):
        csv_path = 'comp3014j/partA_goodput_plr.csv'
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Variant', 'Goodput (Mbps)', 'PLR (%)'])
        for variant in variants:
            writer.writerow([
                variant,
                f"{results[variant]['goodput']:.2f}",
                f"{results[variant]['plr']:.4f}"
            ])
    
    print(f"\nCSV已保存: {csv_path}")
    
    # 3. 绘制对比图 (4个子图: 吞吐量、PLR、公平性、稳定性)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # 准备所有数据
    goodputs = [results[v]['goodput'] for v in variants]
    plrs = [results[v]['plr'] for v in variants]
    fairness_vals = [results[v]['fairness'] for v in variants]
    cov_vals = [results[v]['cov'] for v in variants]
    
    metrics_data = [goodputs, plrs, fairness_vals, cov_vals]
    titles = ['Goodput Comparison', 'Packet Loss Rate Comparison', 
              'Fairness Index Comparison', 'Stability (CoV) Comparison']
    ylabels = ['Goodput (Mbps)', 'PLR (%)', 'Fairness Index', 'CoV']
    formats = ['{:.1f}', '{:.3f}', '{:.4f}', '{:.4f}']
    
    for idx, (data, title, ylabel, fmt) in enumerate(zip(metrics_data, titles, ylabels, formats)):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        bars = ax.bar(variants, data, color=colors, alpha=0.8, 
                     edgecolor='black', linewidth=1.5)
        ax.set_ylabel(ylabel, fontsize=13, fontweight='bold')
        ax.set_xlabel('TCP Variants', fontsize=13, fontweight='bold')
        ax.set_title(title, fontsize=15, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Add value labels on top of bars
        for bar, val in zip(bars, data):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   fmt.format(val),
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Adjust layout to prevent overlap
    plt.tight_layout(pad=3.0)
    
    img_path = 'partA_comparison.png'
    if os.path.exists('comp3014j'):
        img_path = 'comp3014j/partA_comparison.png'
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n图表已保存: {img_path}")
    
    # 4. 公平性分析
    print("\n表格 2: Jain公平性指数 (最后1/3时间)")
    print("-" * 60)
    print(f"{'变体':<10} {'公平性指数':<15}")
    print("-" * 60)
    fairness_values = []
    for variant in variants:
        fairness = results[variant]['fairness']
        fairness_values.append(fairness)
        print(f"{variant:<10} {fairness:<15.4f}")
    print("-" * 60)
    
    best_fairness_idx = fairness_values.index(max(fairness_values))
    best_fairness_variant = variants[best_fairness_idx]
    
    print(f"\n最公平的变体: {best_fairness_variant.upper()} (指数: {fairness_values[best_fairness_idx]:.4f})")
    print("\n公平性分析:")
    print(f"{best_fairness_variant.upper()} 表现出最高的公平性指数,这意味着两个流之间")
    print(f"的带宽分配最为均衡。Jain公平性指数接近1表示资源分配非常公平。")
    print(f"相比之下,其他变体可能因为其拥塞控制机制的差异,导致某个流")
    print(f"获得了更多的带宽,从而降低了整体公平性。")
    
    # 5. 稳定性分析 (CoV)
    print("\n表格 3: 吞吐量稳定性 (变异系数 CoV)")
    print("-" * 60)
    print(f"{'变体':<10} {'CoV':<15}")
    print("-" * 60)
    cov_values = []
    for variant in variants:
        cov = results[variant]['cov']
        cov_values.append(cov)
        print(f"{variant:<10} {cov:<15.4f}")
    print("-" * 60)
    
    best_stability_idx = cov_values.index(min(cov_values))
    best_stability_variant = variants[best_stability_idx]
    
    print(f"\n最稳定的变体: {best_stability_variant.upper()} (CoV: {cov_values[best_stability_idx]:.4f})")
    print("\n稳定性分析:")
    print(f"{best_stability_variant.upper()} 具有最低的变异系数,表明其吞吐量最稳定。")
    print(f"这与其拥塞控制算法的增长和退避逻辑密切相关。较低的CoV意味着")
    print(f"吞吐量波动较小,网络性能更可预测。这种稳定性通常源于更保守的")
    print(f"窗口增长策略或更平滑的退避机制。")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("Part A 总结")
    print("=" * 60)
    
    # 找出最佳算法
    best_goodput_idx = goodputs.index(max(goodputs))
    best_goodput_variant = variants[best_goodput_idx]
    
    print(f"\n在当前设置下,{best_goodput_variant.upper()} 算法表现最佳。")
    print(f"主要原因包括:")
    print(f"1. 吞吐量最高 ({results[best_goodput_variant]['goodput']:.2f} Mbps)")
    print(f"2. 包丢失率为 {results[best_goodput_variant]['plr']:.4f}%")
    print(f"3. 公平性指数为 {results[best_goodput_variant]['fairness']:.4f}")
    print(f"4. 稳定性(CoV)为 {results[best_goodput_variant]['cov']:.4f}")
    print(f"\n综合考虑吞吐量、公平性和稳定性,{best_goodput_variant.upper()} 在这个")
    print(f"特定拓扑和流量模式下提供了最优的性能平衡。")


def run_part_b():
    """
    Part B: DropTail vs RED队列算法比较
    """
    print("\n\n" + "=" * 60)
    print("Part B: DropTail vs RED 队列算法比较")
    print("=" * 60)
    
    # 注意: 需要先运行带有RED的仿真
    # 这里假设已经生成了RED的trace文件 (命名为 *Trace_red.tr)
    
    variants = ['reno', 'cubic', 'vegas', 'yeah']
    
    # DropTail结果 (默认)
    droptail_results = {}
    for variant in variants:
        trace_file = f'comp3014j/{variant}Trace.tr'
        if not os.path.exists(trace_file):
            trace_file = f'{variant}Trace.tr'
        
        print(f"\n处理 {variant.upper()} (DropTail)...")
        analyzer = TCPAnalyzer(trace_file, variant)
        analyzer.parse_trace()
        
        droptail_results[variant] = {
            'goodput': analyzer.get_total_goodput(),
            'plr': analyzer.get_plr(),
            'fairness': analyzer.get_fairness_index(),
            'cov': analyzer.get_stability_cov()
        }
    
    # RED结果 (假设文件名为 *Trace_red.tr)
    red_results = {}
    red_available = True
    for variant in variants:
        trace_file = f'comp3014j/{variant}Trace_red.tr'
        if not os.path.exists(trace_file):
            trace_file = f'{variant}Trace_red.tr'
        
        if not os.path.exists(trace_file):
            print(f"\n警告: 未找到RED trace文件")
            print(f"请先运行带RED队列的仿真,或使用 run_all.sh/run_all.bat 脚本")
            red_available = False
            break
        
        print(f"处理 {variant.upper()} (RED)...")
        analyzer = TCPAnalyzer(trace_file, variant)
        analyzer.parse_trace()
        
        red_results[variant] = {
            'goodput': analyzer.get_total_goodput(),
            'plr': analyzer.get_plr(),
            'fairness': analyzer.get_fairness_index(),
            'cov': analyzer.get_stability_cov()
        }
    
    if not red_available:
        print("\n请按照以下步骤生成RED trace文件:")
        print("1. 修改TCL文件中的队列类型为RED")
        print("2. 重新运行仿真")
        print("3. 将生成的trace文件重命名为 *Trace_red.tr")
        return
    
    # 计算平均值
    dt_avg_goodput = np.mean([droptail_results[v]['goodput'] for v in variants])
    dt_avg_plr = np.mean([droptail_results[v]['plr'] for v in variants])
    dt_avg_fairness = np.mean([droptail_results[v]['fairness'] for v in variants])
    dt_avg_cov = np.mean([droptail_results[v]['cov'] for v in variants])
    
    red_avg_goodput = np.mean([red_results[v]['goodput'] for v in variants])
    red_avg_plr = np.mean([red_results[v]['plr'] for v in variants])
    red_avg_fairness = np.mean([red_results[v]['fairness'] for v in variants])
    red_avg_cov = np.mean([red_results[v]['cov'] for v in variants])
    
    # 打印对比表格
    print("\n表格: DropTail vs RED 性能对比")
    print("-" * 80)
    print(f"{'指标':<20} {'DropTail':<25} {'RED':<25}")
    print("-" * 80)
    print(f"{'平均吞吐量 (Mbps)':<20} {dt_avg_goodput:<25.2f} {red_avg_goodput:<25.2f}")
    print(f"{'平均PLR (%)':<20} {dt_avg_plr:<25.4f} {red_avg_plr:<25.4f}")
    print(f"{'平均公平性':<20} {dt_avg_fairness:<25.4f} {red_avg_fairness:<25.4f}")
    print(f"{'平均稳定性(CoV)':<20} {dt_avg_cov:<25.4f} {red_avg_cov:<25.4f}")
    print("-" * 80)
    
    # Plot comparison charts
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    metrics = ['goodput', 'plr', 'fairness', 'cov']
    titles = ['Goodput (Mbps)', 'Packet Loss Rate (%)', 'Fairness Index', 'Stability (CoV)']
    ylabels = ['Goodput (Mbps)', 'PLR (%)', 'Fairness Index', 'CoV']
    
    for idx, (metric, title, ylabel) in enumerate(zip(metrics, titles, ylabels)):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        dt_values = [droptail_results[v][metric] for v in variants]
        red_values = [red_results[v][metric] for v in variants]
        
        x = np.arange(len(variants))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, dt_values, width, label='DropTail', 
                      color='#1f77b4', alpha=0.8, edgecolor='black', linewidth=1.2)
        bars2 = ax.bar(x + width/2, red_values, width, label='RED', 
                      color='#ff7f0e', alpha=0.8, edgecolor='black', linewidth=1.2)
        
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_xlabel('TCP Variants', fontsize=12, fontweight='bold')
        ax.set_title(f'{title} Comparison: DropTail vs RED', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(variants, fontsize=11)
        ax.legend(fontsize=11, loc='best')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
    
    plt.tight_layout(pad=3.0)
    
    img_path = 'partB_comparison.png'
    if os.path.exists('comp3014j'):
        img_path = 'comp3014j/partB_comparison.png'
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n图表已保存: {img_path}")
    
    # 分析和解释
    print("\n解释:")
    print(f"DropTail和RED在性能上的主要差异体现在包丢失模式和队列管理策略上。")
    print(f"RED通过主动的早期随机丢包,可以在队列填满前就开始丢包,从而:")
    print(f"1. 减少全局同步现象 (多个TCP流同时进入慢启动)")
    print(f"2. 降低平均队列长度,减少延迟")
    print(f"3. 提供更平滑的丢包模式")
    print(f"\nDropTail则是被动的尾部丢包,只在队列满时才丢包,可能导致:")
    print(f"1. 突发性的大量丢包")
    print(f"2. TCP流的全局同步")
    print(f"3. 较高的队列延迟")


def run_part_c():
    """
    Part C: 可重复性测试
    """
    print("\n\n" + "=" * 60)
    print("Part C: 可重复性测试")
    print("=" * 60)
    
    print("\n说明: Part C需要运行多次仿真(不同随机种子)")
    print("请使用提供的shell脚本来生成多次运行的结果。")
    print("\n示例: 对于cubic变体,运行5次:")
    print("  运行1: cubicTrace_run1.tr")
    print("  运行2: cubicTrace_run2.tr")
    print("  ...")
    print("  运行5: cubicTrace_run5.tr")
    
    # 检查是否有多次运行的文件
    variant = 'cubic'  # 选择最有趣的变体
    num_runs = 5
    
    goodputs = []
    plrs = []
    fairness_values = []
    cov_values = []
    
    all_runs_available = True
    
    for run_idx in range(1, num_runs + 1):
        trace_file = f'comp3014j/{variant}Trace_run{run_idx}.tr'
        if not os.path.exists(trace_file):
            trace_file = f'{variant}Trace_run{run_idx}.tr'
        
        if not os.path.exists(trace_file):
            all_runs_available = False
            break
        
        print(f"处理运行 {run_idx}/{num_runs}...")
        analyzer = TCPAnalyzer(trace_file, variant)
        analyzer.parse_trace()
        
        goodputs.append(analyzer.get_total_goodput())
        plrs.append(analyzer.get_plr())
        fairness_values.append(analyzer.get_fairness_index())
        cov_values.append(analyzer.get_stability_cov())
    
    if not all_runs_available:
        print(f"\n警告: 未找到所有运行的trace文件")
        print(f"需要文件: {variant}Trace_run1.tr 到 {variant}Trace_run{num_runs}.tr")
        return
    
    # 计算统计量
    goodput_mean = np.mean(goodputs)
    goodput_std = np.std(goodputs)
    goodput_ci = 1.96 * goodput_std  # 95% 置信区间
    
    plr_mean = np.mean(plrs)
    plr_std = np.std(plrs)
    plr_ci = 1.96 * plr_std
    
    # 打印结果
    print(f"\n{variant.upper()} 变体 - {num_runs}次运行的统计结果:")
    print("-" * 60)
    print(f"{'指标':<20} {'均值':<15} {'标准差':<15} {'95% CI':<15}")
    print("-" * 60)
    print(f"{'吞吐量 (Mbps)':<20} {goodput_mean:<15.2f} {goodput_std:<15.2f} ±{goodput_ci:<15.2f}")
    print(f"{'PLR (%)':<20} {plr_mean:<15.4f} {plr_std:<15.4f} ±{plr_ci:<15.4f}")
    print("-" * 60)
    
    # Plot detailed charts showing all 5 runs + mean with error bars
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Subplot 1: Goodput - Individual runs with mean line
    x_pos = np.arange(len(goodputs))
    bars1 = axes[0, 0].bar(x_pos, goodputs, color='#1f77b4', alpha=0.7, 
                           edgecolor='black', linewidth=1.5, width=0.6)
    axes[0, 0].axhline(y=goodput_mean, color='red', linestyle='--', 
                       linewidth=2.5, label=f'Mean: {goodput_mean:.2f} Mbps')
    axes[0, 0].fill_between([-0.5, len(goodputs)-0.5], 
                            goodput_mean - goodput_ci, 
                            goodput_mean + goodput_ci,
                            alpha=0.2, color='red', label='95% CI')
    axes[0, 0].set_ylabel('Goodput (Mbps)', fontsize=13, fontweight='bold')
    axes[0, 0].set_xlabel('Run Number', fontsize=13, fontweight='bold')
    axes[0, 0].set_title(f'{variant.upper()} - Goodput Across 5 Runs', 
                        fontsize=14, fontweight='bold')
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels([f'Run {i+1}' for i in range(len(goodputs))], fontsize=11)
    axes[0, 0].legend(loc='best', fontsize=11)
    axes[0, 0].grid(axis='y', alpha=0.3, linestyle='--')
    axes[0, 0].set_axisbelow(True)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, goodputs)):
        height = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.1f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Subplot 2: Goodput - Mean with 95% CI error bars
    axes[0, 1].bar(['Mean Goodput'], [goodput_mean], yerr=[goodput_ci], 
                   color='#1f77b4', alpha=0.8, edgecolor='black', 
                   linewidth=2, capsize=20, error_kw={'linewidth': 3, 'capthick': 3},
                   width=0.4)
    axes[0, 1].set_ylabel('Goodput (Mbps)', fontsize=13, fontweight='bold')
    axes[0, 1].set_title(f'{variant.upper()} - Mean Goodput ± 95% CI', 
                        fontsize=14, fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3, linestyle='--')
    axes[0, 1].set_axisbelow(True)
    
    # Add detailed statistics
    stats_text = f'Mean: {goodput_mean:.2f}\nStd: {goodput_std:.2f}\n95% CI: ±{goodput_ci:.2f}'
    axes[0, 1].text(0.5, 0.95, stats_text, transform=axes[0, 1].transAxes,
                   fontsize=11, verticalalignment='top', horizontalalignment='center',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Subplot 3: PLR - Individual runs with mean line
    bars3 = axes[1, 0].bar(x_pos, plrs, color='#ff7f0e', alpha=0.7, 
                           edgecolor='black', linewidth=1.5, width=0.6)
    axes[1, 0].axhline(y=plr_mean, color='red', linestyle='--', 
                       linewidth=2.5, label=f'Mean: {plr_mean:.4f}%')
    axes[1, 0].fill_between([-0.5, len(plrs)-0.5], 
                            plr_mean - plr_ci, 
                            plr_mean + plr_ci,
                            alpha=0.2, color='red', label='95% CI')
    axes[1, 0].set_ylabel('Packet Loss Rate (%)', fontsize=13, fontweight='bold')
    axes[1, 0].set_xlabel('Run Number', fontsize=13, fontweight='bold')
    axes[1, 0].set_title(f'{variant.upper()} - PLR Across 5 Runs', 
                        fontsize=14, fontweight='bold')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels([f'Run {i+1}' for i in range(len(plrs))], fontsize=11)
    axes[1, 0].legend(loc='best', fontsize=11)
    axes[1, 0].grid(axis='y', alpha=0.3, linestyle='--')
    axes[1, 0].set_axisbelow(True)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars3, plrs)):
        height = bar.get_height()
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.3f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Subplot 4: PLR - Mean with 95% CI error bars
    axes[1, 1].bar(['Mean PLR'], [plr_mean], yerr=[plr_ci], 
                   color='#ff7f0e', alpha=0.8, edgecolor='black', 
                   linewidth=2, capsize=20, error_kw={'linewidth': 3, 'capthick': 3},
                   width=0.4)
    axes[1, 1].set_ylabel('Packet Loss Rate (%)', fontsize=13, fontweight='bold')
    axes[1, 1].set_title(f'{variant.upper()} - Mean PLR ± 95% CI', 
                        fontsize=14, fontweight='bold')
    axes[1, 1].grid(axis='y', alpha=0.3, linestyle='--')
    axes[1, 1].set_axisbelow(True)
    
    # Add detailed statistics
    stats_text = f'Mean: {plr_mean:.4f}\nStd: {plr_std:.4f}\n95% CI: ±{plr_ci:.4f}'
    axes[1, 1].text(0.5, 0.95, stats_text, transform=axes[1, 1].transAxes,
                   fontsize=11, verticalalignment='top', horizontalalignment='center',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(pad=3.0)
    
    img_path = 'partC_reproducibility.png'
    if os.path.exists('comp3014j'):
        img_path = 'comp3014j/partC_reproducibility.png'
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n图表已保存: {img_path}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("TCP性能分析器 - analyser3.py")
    print("=" * 60)
    
    # Part A: TCP变体分析
    run_part_a()
    
    # Part B: DropTail vs RED
    run_part_b()
    
    # Part C: 可重复性
    run_part_c()
    
    print("\n\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print("\n生成的文件:")
    print("  - partA_goodput_plr.csv")
    print("  - partA_comparison.png")
    print("  - partB_comparison.png")
    print("  - partC_reproducibility.png")
    print("=" * 60)


if __name__ == '__main__':
    main()

