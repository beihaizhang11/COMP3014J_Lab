#!/bin/bash
# 只运行分析脚本 (假设trace文件已经存在)

echo "=========================================="
echo "TCP性能分析 - 仅运行分析"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "工作目录: $(pwd)"
echo ""

# 检查必需的trace文件
echo "检查trace文件..."
missing_files=0

for variant in reno cubic vegas yeah; do
    if [ ! -f "${variant}Trace.tr" ]; then
        echo "  ✗ ${variant}Trace.tr 不存在"
        missing_files=$((missing_files + 1))
    else
        echo "  ✓ ${variant}Trace.tr ($(du -h ${variant}Trace.tr | cut -f1))"
    fi
done

if [ $missing_files -gt 0 ]; then
    echo ""
    echo "警告: 缺少 $missing_files 个DropTail trace文件"
    echo "请先运行: ns renoCode.tcl 等仿真命令"
    echo ""
fi

# 检查RED trace文件
echo ""
echo "检查RED trace文件..."
red_files=0
for variant in reno cubic vegas yeah; do
    if [ -f "${variant}Trace_red.tr" ]; then
        echo "  ✓ ${variant}Trace_red.tr"
        red_files=$((red_files + 1))
    fi
done

if [ $red_files -eq 0 ]; then
    echo "  ! 没有找到RED trace文件 (Part B将跳过)"
fi

# 检查可重复性测试文件
echo ""
echo "检查可重复性测试文件..."
run_files=$(ls -1 cubicTrace_run*.tr 2>/dev/null | wc -l)
echo "  找到 $run_files 个运行文件"

if [ $run_files -lt 5 ]; then
    echo "  ! 需要5个文件进行Part C分析"
fi

# 运行分析
echo ""
echo "=========================================="
echo "运行 analyser3.py..."
echo "=========================================="
echo ""

python3 analyser3.py

exit_code=$?

echo ""
echo "=========================================="
echo "分析完成 (退出码: $exit_code)"
echo "=========================================="

# 显示生成的文件
echo ""
echo "生成的文件:"
echo ""

if [ -f "partA_comparison.png" ]; then
    echo "✓ partA_comparison.png ($(du -h partA_comparison.png | cut -f1))"
    echo "  位置: $(pwd)/partA_comparison.png"
else
    echo "✗ partA_comparison.png 未生成"
fi

echo ""

if [ -f "partB_comparison.png" ]; then
    echo "✓ partB_comparison.png ($(du -h partB_comparison.png | cut -f1))"
    echo "  位置: $(pwd)/partB_comparison.png"
else
    echo "✗ partB_comparison.png 未生成"
fi

echo ""

if [ -f "partC_reproducibility.png" ]; then
    echo "✓ partC_reproducibility.png ($(du -h partC_reproducibility.png | cut -f1))"
    echo "  位置: $(pwd)/partC_reproducibility.png"
else
    echo "✗ partC_reproducibility.png 未生成"
fi

echo ""

if [ -f "partA_goodput_plr.csv" ]; then
    echo "✓ partA_goodput_plr.csv ($(wc -l < partA_goodput_plr.csv) 行)"
    echo "  位置: $(pwd)/partA_goodput_plr.csv"
    echo ""
    echo "  内容预览:"
    head -5 partA_goodput_plr.csv | sed 's/^/    /'
else
    echo "✗ partA_goodput_plr.csv 未生成"
fi

echo ""
echo "=========================================="
echo "查看图片:"
echo "  使用文件管理器打开当前目录"
echo "  或使用: eog *.png"
echo "  或使用: xdg-open partA_comparison.png"
echo "=========================================="

