#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证analyser3.py能否正确解析trace文件
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyser3 import TCPAnalyzer

def test_trace_parsing():
    """测试trace文件解析"""
    print("=" * 60)
    print("测试 trace 文件解析")
    print("=" * 60)
    
    variants = ['reno', 'cubic', 'vegas', 'yeah']
    
    for variant in variants:
        # 尝试两种路径
        trace_file = f'{variant}Trace.tr'
        if not os.path.exists(trace_file):
            trace_file = f'comp3014j/{variant}Trace.tr'
        
        if not os.path.exists(trace_file):
            print(f"\n警告: 未找到 {variant}Trace.tr")
            print(f"请先运行仿真: ns {variant}Code.tcl")
            continue
        
        print(f"\n测试 {variant.upper()}:")
        print(f"  文件: {trace_file}")
        print(f"  大小: {os.path.getsize(trace_file) / 1024:.2f} KB")
        
        # 解析
        analyzer = TCPAnalyzer(trace_file, variant)
        analyzer.parse_trace()
        
        # 显示结果
        print(f"  Flow 1 发送包: {analyzer.flow1_data['sent_packets']}")
        print(f"  Flow 1 接收包: {analyzer.flow1_data['rcvd_packets']}")
        print(f"  Flow 1 丢包: {analyzer.flow1_data['dropped_packets']}")
        print(f"  Flow 2 发送包: {analyzer.flow2_data['sent_packets']}")
        print(f"  Flow 2 接收包: {analyzer.flow2_data['rcvd_packets']}")
        print(f"  Flow 2 丢包: {analyzer.flow2_data['dropped_packets']}")
        
        goodput = analyzer.get_total_goodput()
        plr = analyzer.get_plr()
        fairness = analyzer.get_fairness_index()
        cov = analyzer.get_stability_cov()
        
        print(f"  总吞吐量: {goodput:.2f} Mbps")
        print(f"  PLR: {plr:.4f}%")
        print(f"  公平性指数: {fairness:.4f}")
        print(f"  稳定性(CoV): {cov:.4f}")
        
        if goodput == 0:
            print(f"  ⚠ 警告: 吞吐量为0,可能解析有问题")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_trace_parsing()

