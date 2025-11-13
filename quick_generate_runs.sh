#!/bin/bash
# 快速生成5次Reno运行的脚本

echo "=========================================="
echo "快速生成 Cubic 的 5 次运行"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "当前目录: $(pwd)"
echo ""

# 检查cubicCode.tcl是否存在
if [ ! -f "cubicCode.tcl" ]; then
    echo "错误: 找不到 cubicCode.tcl"
    exit 1
fi

# 删除旧文件
echo "清理旧文件..."
rm -f cubicTrace_run*.tr cubic_run*.nam cubicCode_run*.tcl

echo ""
echo "开始生成 5 次运行..."
echo "------------------------------------------"

for run_idx in {1..5}; do
    echo ""
    echo "=== 运行 $run_idx/5 ==="
    
    temp_file="cubicCode_run${run_idx}.tcl"
    trace_output="cubicTrace_run${run_idx}.tr"
    nam_output="cubic_run${run_idx}.nam"
    
    # 计算随机种子
    seed=$((run_idx * 12345 + 6789))
    
    # 计算启动时间抖动
    jitter1=$(awk -v seed=$seed 'BEGIN{srand(seed); printf "%.6f", rand() * 0.5}')
    jitter2=$(awk -v seed=$((seed+999)) 'BEGIN{srand(seed+999); printf "%.6f", rand() * 0.5}')
    
    echo "配置:"
    echo "  随机种子: $seed"
    echo "  FTP1启动抖动: $jitter1 秒"
    echo "  FTP2启动抖动: $jitter2 秒"
    
    # 使用awk修改TCL文件
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
        # 修改FTP1启动时间
        if ($0 ~ /\$ns at 0\.0 "\$myftp1 start"/) {
            print "$ns at " jitter1 " \"$myftp1 start\""
            next
        }
        # 修改FTP2启动时间
        if ($0 ~ /\$ns at 0\.0 "\$myftp2 start"/) {
            print "$ns at " jitter2 " \"$myftp2 start\""
            next
        }
        print $0
    }' cubicCode.tcl > "$temp_file"
    
    echo ""
    echo "生成的TCL文件: $temp_file"
    echo "运行NS2仿真..."
    
    # 运行仿真
    ns "$temp_file" 2>&1 | head -5
    
    # 检查结果
    if [ -f "$trace_output" ]; then
        size=$(du -h "$trace_output" | cut -f1)
        lines=$(wc -l < "$trace_output")
        echo "✓ 成功! $trace_output"
        echo "  文件大小: $size"
        echo "  行数: $lines"
    else
        echo "✗ 失败! 未生成 $trace_output"
        echo "检查NS2是否正确安装: which ns"
        exit 1
    fi
    
    # 保留第一个临时文件用于检查,删除其余
    if [ $run_idx -ne 1 ]; then
        rm -f "$temp_file"
    fi
done

echo ""
echo "=========================================="
echo "验证生成的文件"
echo "=========================================="
echo ""

# 列出所有生成的文件
echo "生成的trace文件:"
ls -lh cubicTrace_run*.tr 2>/dev/null | awk '{print "  " $9 " - " $5}'

echo ""
echo "文件大小对比:"
for i in {1..5}; do
    if [ -f "cubicTrace_run$i.tr" ]; then
        size=$(stat -f%z "cubicTrace_run$i.tr" 2>/dev/null || stat -c%s "cubicTrace_run$i.tr" 2>/dev/null)
        echo "  Run $i: $size bytes"
    fi
done

echo ""
echo "检查第一个临时TCL文件 (用于验证配置):"
if [ -f "cubicCode_run1.tcl" ]; then
    echo "  文件: cubicCode_run1.tcl"
    echo ""
    echo "  随机种子部分:"
    grep -A 10 "Random seed" cubicCode_run1.tcl | head -12
    echo ""
    echo "  启动时间部分:"
    grep "myftp.*start" cubicCode_run1.tcl
fi

echo ""
echo "=========================================="
echo "完成!"
echo "=========================================="
echo ""
echo "现在运行分析:"
echo "  python3 analyser3.py"
echo ""
echo "查看结果:"
echo "  eog partC_reproducibility.png"
echo ""

