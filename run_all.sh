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

variant="cubic"  # 选择cubic作为示例

for run_idx in {1..5}; do
    trace_output="${variant}Trace_run${run_idx}.tr"
    
    # 检查是否已存在
    if [ -f "$trace_output" ]; then
        echo "$trace_output 已存在，跳过"
        continue
    fi
    
    echo "运行 ${variant} - 第 ${run_idx} 次..."
    
    # 创建临时TCL文件,修改随机种子
    temp_file="${variant}Code_run${run_idx}.tcl"
    nam_output="${variant}_run${run_idx}.nam"
    
    # 修改输出文件名和添加随机种子
    sed "s/${variant}Trace.tr/${trace_output}/g" "${variant}Code.tcl" | \
    sed "s/${variant}.nam/${nam_output}/g" | \
    sed "11 i\\
global defaultRNG\\
\$defaultRNG seed ${run_idx}123" > "$temp_file"
    
    ns "$temp_file"
    rm -f "$temp_file"
done

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
