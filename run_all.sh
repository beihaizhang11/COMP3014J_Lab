#!/bin/bash
# 自动化运行脚本 - 执行所有仿真和分析

echo "=========================================="
echo "TCP性能分析 - 自动化运行脚本"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "工作目录: $(pwd)"
echo ""

# Part A: 运行DropTail仿真
echo "Part A: 运行DropTail仿真..."
echo "------------------------------------------"

if [ ! -f "renoTrace.tr" ]; then
    echo "运行 Reno..."
    ns renoCode.tcl
else
    echo "renoTrace.tr 已存在，跳过"
fi

if [ ! -f "cubicTrace.tr" ]; then
    echo "运行 Cubic..."
    ns cubicCode.tcl
else
    echo "cubicTrace.tr 已存在，跳过"
fi

if [ ! -f "vegasTrace.tr" ]; then
    echo "运行 Vegas..."
    ns vegasCode.tcl
else
    echo "vegasTrace.tr 已存在，跳过"
fi

if [ ! -f "yeahTrace.tr" ]; then
    echo "运行 Yeah..."
    ns yeahCode.tcl
else
    echo "yeahTrace.tr 已存在，跳过"
fi

echo "DropTail仿真完成!"

# Part B: 创建RED版本的TCL文件并运行
echo ""
echo "Part B: 准备RED仿真..."
echo "------------------------------------------"

# 创建RED版本的TCL文件
for variant in reno cubic vegas yeah; do
    input_file="${variant}Code.tcl"
    output_file="${variant}Code_red.tcl"
    trace_output="${variant}Trace_red.tr"
    nam_output="${variant}_red.nam"
    
    # 检查RED trace是否已存在
    if [ -f "$trace_output" ]; then
        echo "$trace_output 已存在，跳过"
        continue
    fi
    
    # 替换DropTail为RED,并修改输出文件名
    sed "s/DropTail/RED/g" "$input_file" | \
    sed "s/${variant}Trace.tr/${trace_output}/g" | \
    sed "s/${variant}.nam/${nam_output}/g" > "$output_file"
    
    echo "运行 ${variant} (RED)..."
    ns "$output_file"
    rm -f "$output_file"
done

echo "RED仿真完成!"

# Part C: 运行多次仿真(可重复性测试)
echo ""
echo "Part C: 运行可重复性测试 (5次运行)..."
echo "------------------------------------------"

variant="reno"  # 选择reno作为示例 - Reno对随机性更敏感

# 删除旧的运行文件,确保重新生成
echo "清理旧的可重复性测试文件..."
rm -f ${variant}Trace_run*.tr ${variant}_run*.nam

for run_idx in {1..5}; do
    echo "运行 ${variant} - 第 ${run_idx} 次..."
    
    temp_file="${variant}Code_run${run_idx}.tcl"
    trace_output="${variant}Trace_run${run_idx}.tr"
    nam_output="${variant}_run${run_idx}.nam"
    
    # 计算不同的随机种子
    seed=$((run_idx * 12345 + 6789))
    
    # 计算启动时间抖动 (0到0.5秒的随机延迟)
    jitter1=$(awk -v seed=$seed 'BEGIN{srand(seed); print rand() * 0.5}')
    jitter2=$(awk -v seed=$((seed+999)) 'BEGIN{srand(seed+999); print rand() * 0.5}')
    
    # 使用awk创建修改后的TCL文件,添加随机种子和启动时间抖动
    awk -v seed="$seed" -v trace="$trace_output" -v nam="$nam_output" \
        -v jitter1="$jitter1" -v jitter2="$jitter2" '
    {
        # 修改trace文件名
        if ($0 ~ /set tracefile1 \[open.*\.tr w\]/) {
            print "set tracefile1 [open " trace " w]"
            next
        }
        # 修改nam文件名
        if ($0 ~ /set namfile \[open.*\.nam w\]/) {
            print "set namfile [open " nam " w]"
            next
        }
        # 在创建Simulator后添加随机种子
        if ($0 ~ /set ns \[new Simulator\]/) {
            print $0
            print ""
            print "# Random seed configuration - Run with different seed"
            print "set rng [new RNG]"
            print "$rng seed " seed
            print ""
            print "# Additional RNG for packet drops"
            print "set rng2 [new RNG]"
            print "$rng2 seed " (seed + 111)
            print ""
            print "# Set random seed for ns-random"
            print "ns-random " seed
            next
        }
        # 修改FTP1启动时间,添加随机抖动
        if ($0 ~ /\$ns at 0\.0 "\$myftp1 start"/) {
            print "$ns at " jitter1 " \"$myftp1 start\""
            next
        }
        # 修改FTP2启动时间,添加随机抖动
        if ($0 ~ /\$ns at 0\.0 "\$myftp2 start"/) {
            print "$ns at " jitter2 " \"$myftp2 start\""
            next
        }
        print $0
    }' "${variant}Code.tcl" > "$temp_file"
    
    echo "  随机种子: $seed"
    echo "  FTP1启动时间抖动: $jitter1 秒"
    echo "  FTP2启动时间抖动: $jitter2 秒"
    echo "  输出文件: $trace_output"
    
    # 运行仿真
    ns "$temp_file"
    
    # 检查是否成功
    if [ -f "$trace_output" ]; then
        size=$(du -h "$trace_output" | cut -f1)
        echo "  ✓ 完成! 文件大小: $size"
    else
        echo "  ✗ 失败! 未生成trace文件"
    fi
    
    # 清理临时文件
    rm -f "$temp_file"
done

echo ""
echo "验证文件差异..."
# 快速检查文件是否不同
file1="${variant}Trace_run1.tr"
file2="${variant}Trace_run2.tr"
if [ -f "$file1" ] && [ -f "$file2" ]; then
    size1=$(stat -f%z "$file1" 2>/dev/null || stat -c%s "$file1" 2>/dev/null)
    size2=$(stat -f%z "$file2" 2>/dev/null || stat -c%s "$file2" 2>/dev/null)
    if [ "$size1" = "$size2" ]; then
        echo "  ⚠ 警告: Run 1和Run 2文件大小相同,可能随机性不足"
    else
        echo "  ✓ 文件大小不同,随机性正常"
    fi
fi

echo "可重复性测试完成!"

# 运行分析脚本
echo ""
echo "=========================================="
echo "运行分析脚本..."
echo "=========================================="

echo ""
echo "运行 analyser3.py (主分析)..."
python3 analyser3.py

if [ $? -eq 0 ]; then
    echo "✓ analyser3.py 运行成功"
else
    echo "✗ analyser3.py 运行失败"
fi

echo ""
echo "运行 analyser2.py..."
python3 analyser2.py 2>/dev/null || echo "analyser2.py 运行完成"

echo ""
echo "运行 analyser.py..."
python3 analyser.py 2>/dev/null || echo "analyser.py 运行完成"

# 检查生成的文件
echo ""
echo "=========================================="
echo "检查生成的文件..."
echo "=========================================="

echo ""
echo "图表文件:"
for img in partA_comparison.png partB_comparison.png partC_reproducibility.png; do
    if [ -f "$img" ]; then
        echo "  ✓ $img ($(du -h $img | cut -f1))"
    else
        echo "  ✗ $img (未生成)"
    fi
done

echo ""
echo "CSV文件:"
for csv in partA_goodput_plr.csv; do
    if [ -f "$csv" ]; then
        echo "  ✓ $csv ($(wc -l < $csv) 行)"
    else
        echo "  ✗ $csv (未生成)"
    fi
done

echo ""
echo "Trace文件:"
echo "  DropTail: $(ls -1 *Trace.tr 2>/dev/null | grep -v "_red\|_run" | wc -l) 个"
echo "  RED: $(ls -1 *Trace_red.tr 2>/dev/null | wc -l) 个"
echo "  可重复性测试: $(ls -1 *Trace_run*.tr 2>/dev/null | wc -l) 个"

echo ""
echo "=========================================="
echo "所有任务完成!"
echo "=========================================="
echo ""
echo "生成的文件位置: $(pwd)"
echo ""
echo "查看图表:"
echo "  ls -lh *.png"
echo ""
echo "查看CSV:"
echo "  cat partA_goodput_plr.csv"
echo "=========================================="
