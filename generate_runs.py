#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成5次不同的cubic运行
使用不同的参数来保证结果不同
"""

import os
import subprocess
import random

def modify_tcl_for_run(input_file, output_file, trace_file, nam_file, run_number):
    """
    修改TCL文件以生成不同的运行
    
    策略:
    1. 修改随机种子 (多种方式)
    2. 修改启动时间(添加随机抖动)
    3. 修改输出文件名
    """
    with open(input_file, 'r') as f:
        content = f.read()
    
    # 生成不同的随机种子
    seed = run_number * 12345 + 6789
    
    # 生成启动时间抖动 (0-0.5秒)
    random.seed(seed)
    jitter1 = random.uniform(0, 0.5)
    jitter2 = random.uniform(0, 0.5)
    
    # 替换输出文件名
    variant = 'reno' if 'reno' in input_file else 'cubic'
    content = content.replace(f'{variant}Trace.tr', trace_file)
    content = content.replace(f'{variant}.nam', nam_file)
    
    # 在 "set ns [new Simulator]" 之后添加随机种子配置
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # 在创建Simulator后添加随机种子
        if 'set ns [new Simulator]' in line:
            new_lines.append('')
            new_lines.append(f'# Random seed configuration - Run {run_number}')
            new_lines.append('set rng [new RNG]')
            new_lines.append(f'$rng seed {seed}')
            new_lines.append('')
            new_lines.append('# Additional RNG for packet drops')
            new_lines.append('set rng2 [new RNG]')
            new_lines.append(f'$rng2 seed {seed + 111}')
            new_lines.append('')
            new_lines.append('# Set random seed for ns-random')
            new_lines.append(f'ns-random {seed}')
        
        # 修改FTP启动时间,添加随机抖动
        if '$ns at 0.0 "$myftp1 start"' in line:
            new_lines[-1] = f'$ns at {jitter1:.6f} "$myftp1 start"'
        elif '$ns at 0.0 "$myftp2 start"' in line:
            new_lines[-1] = f'$ns at {jitter2:.6f} "$myftp2 start"'
    
    # 写入新文件
    with open(output_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"  创建配置文件: {output_file}")
    print(f"  随机种子: {seed}")
    print(f"  FTP1启动抖动: {jitter1:.3f}秒")
    print(f"  FTP2启动抖动: {jitter2:.3f}秒")
    print(f"  输出trace: {trace_file}")

def run_ns2_simulation(tcl_file):
    """运行NS2仿真"""
    try:
        result = subprocess.run(['ns', tcl_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)
        return result.returncode == 0
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    print("=" * 60)
    print("生成5次可重复性测试运行 (Cubic)")
    print("=" * 60)
    
    variant = 'cubic'
    num_runs = 5
    
    # 切换到脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    input_file = f'{variant}Code.tcl'
    
    if not os.path.exists(input_file):
        print(f"错误: 找不到 {input_file}")
        return
    
    print(f"\n使用输入文件: {input_file}\n")
    
    # 生成并运行5次
    for run_idx in range(1, num_runs + 1):
        print(f"\n运行 {run_idx}/{num_runs}:")
        print("-" * 40)
        
        temp_file = f'{variant}Code_run{run_idx}.tcl'
        trace_file = f'{variant}Trace_run{run_idx}.tr'
        nam_file = f'{variant}_run{run_idx}.nam'
        
        # 删除旧文件
        for f in [trace_file, nam_file, temp_file]:
            if os.path.exists(f):
                os.remove(f)
        
        # 修改TCL文件
        modify_tcl_for_run(input_file, temp_file, trace_file, nam_file, run_idx)
        
        # 运行仿真
        print(f"  运行NS2仿真...")
        success = run_ns2_simulation(temp_file)
        
        if success and os.path.exists(trace_file):
            size = os.path.getsize(trace_file)
            print(f"  ✓ 完成! 文件大小: {size/1024:.1f} KB")
        else:
            print(f"  ✗ 失败! 未生成trace文件")
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # 验证文件
    print("\n" + "=" * 60)
    print("验证生成的文件:")
    print("=" * 60)
    
    all_sizes = []
    for run_idx in range(1, num_runs + 1):
        trace_file = f'{variant}Trace_run{run_idx}.tr'
        if os.path.exists(trace_file):
            size = os.path.getsize(trace_file)
            lines = sum(1 for _ in open(trace_file))
            all_sizes.append(size)
            print(f"✓ Run {run_idx}: {size/1024:.1f} KB, {lines} 行")
        else:
            print(f"✗ Run {run_idx}: 文件不存在")
    
    # 检查是否所有文件大小相同(如果相同说明没有变化)
    if all_sizes and len(set(all_sizes)) == 1:
        print("\n⚠ 警告: 所有文件大小相同,可能随机性不足")
    elif all_sizes:
        print(f"\n✓ 文件大小不同,变化范围: {min(all_sizes)/1024:.1f} - {max(all_sizes)/1024:.1f} KB")
    
    print("\n" + "=" * 60)
    print("完成! 现在运行分析:")
    print("  python3 analyser3.py")
    print("=" * 60)

if __name__ == '__main__':
    main()

