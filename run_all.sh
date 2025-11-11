#!/bin/bash
# 自动化运行脚本 - 执行所有仿真和分析

echo "=========================================="
echo "TCP性能分析 - 自动化运行脚本"
echo "=========================================="

cd comp3014j 2>/dev/null || cd .

# Part A: 运行DropTail仿真
echo ""
echo "Part A: 运行DropTail仿真..."
echo "------------------------------------------"

echo "运行 Reno..."
ns renoCode.tcl

echo "运行 Cubic..."
ns cubicCode.tcl

echo "运行 Vegas..."
ns vegasCode.tcl

echo "运行 Yeah..."
ns yeahCode.tcl

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
    
    # 替换DropTail为RED,并修改输出文件名
    sed "s/DropTail/RED/g" "$input_file" | \
    sed "s/${variant}Trace.tr/${trace_output}/g" | \
    sed "s/${variant}.nam/${nam_output}/g" > "$output_file"
    
    echo "创建: $output_file"
done

echo ""
echo "运行RED仿真..."
for variant in reno cubic vegas yeah; do
    echo "运行 ${variant} (RED)..."
    ns "${variant}Code_red.tcl"
done

echo "RED仿真完成!"

# Part C: 运行多次仿真(可重复性测试)
echo ""
echo "Part C: 运行可重复性测试 (5次运行)..."
echo "------------------------------------------"

variant="cubic"  # 选择cubic作为示例

for run_idx in {1..5}; do
    echo "运行 ${variant} - 第 ${run_idx} 次..."
    
    # 创建临时TCL文件,修改随机种子
    temp_file="${variant}Code_run${run_idx}.tcl"
    trace_output="${variant}Trace_run${run_idx}.tr"
    nam_output="${variant}_run${run_idx}.nam"
    
    # 修改输出文件名和添加随机种子
    sed "s/${variant}Trace.tr/${trace_output}/g" "${variant}Code.tcl" | \
    sed "s/${variant}.nam/${nam_output}/g" | \
    sed "11 i\\global defaultRNG\n\$defaultRNG seed ${run_idx}123" > "$temp_file"
    
    ns "$temp_file"
    rm "$temp_file"  # 清理临时文件
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

echo ""
echo "运行 analyser2.py..."
python3 analyser2.py

echo ""
echo "运行 analyser.py..."
python3 analyser.py

# 清理临时文件
echo ""
echo "=========================================="
echo "清理临时文件..."
echo "=========================================="

# 清理RED版本的TCL文件
rm -f *Code_red.tcl

# 清理NAM文件(可选)
# rm -f *.nam

echo ""
echo "=========================================="
echo "所有任务完成!"
echo "=========================================="
echo ""
echo "生成的文件:"
echo "  Trace文件:"
echo "    - *Trace.tr (DropTail)"
echo "    - *Trace_red.tr (RED)"
echo "    - *Trace_run*.tr (可重复性测试)"
echo ""
echo "  CSV文件:"
echo "    - partA_goodput_plr.csv"
echo ""
echo "  图表文件:"
echo "    - partA_comparison.png"
echo "    - partB_comparison.png"
echo "    - partC_reproducibility.png"
echo "=========================================="

