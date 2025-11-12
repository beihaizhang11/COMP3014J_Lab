#!/bin/bash
# 生成5次不同的cubic运行,使用不同的随机种子和网络抖动

echo "=========================================="
echo "生成5次可重复性测试运行 (Reno)"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

variant="reno"

echo ""
echo "为每次运行创建不同的配置..."

for run_idx in {1..5}; do
    echo ""
    echo "准备运行 ${run_idx}/5..."
    
    input_file="${variant}Code.tcl"
    temp_file="${variant}Code_run${run_idx}.tcl"
    trace_output="${variant}Trace_run${run_idx}.tr"
    nam_output="${variant}_run${run_idx}.nam"
    
    # 删除旧文件
    rm -f "$trace_output" "$nam_output"
    
    # 创建修改后的TCL文件
    # 方法: 在set ns [new Simulator]之后添加随机种子
    awk -v seed=$((run_idx * 1234 + 567)) -v trace="$trace_output" -v nam="$nam_output" '
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
            print "# 设置随机种子 - Run " run_idx
            print "set rng [new RNG]"
            print "$rng seed " seed
            print "set defaultRNG $rng"
            next
        }
        print $0
    }' run_idx="$run_idx" "$input_file" > "$temp_file"
    
    echo "  生成配置文件: $temp_file"
    echo "  随机种子: $((run_idx * 1234 + 567))"
    echo "  输出文件: $trace_output"
    
    # 运行仿真
    echo "  运行NS2仿真..."
    ns "$temp_file"
    
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
echo "=========================================="
echo "检查生成的文件..."
echo "=========================================="

echo ""
for run_idx in {1..5}; do
    trace_file="${variant}Trace_run${run_idx}.tr"
    if [ -f "$trace_file" ]; then
        size=$(du -h "$trace_file" | cut -f1)
        lines=$(wc -l < "$trace_file")
        echo "✓ Run ${run_idx}: $trace_file ($size, $lines lines)"
    else
        echo "✗ Run ${run_idx}: $trace_file (不存在)"
    fi
done

echo ""
echo "=========================================="
echo "验证文件是否不同..."
echo "=========================================="

# 比较文件的前100行看是否不同
echo ""
echo "文件差异检查:"
for i in {1..4}; do
    j=$((i + 1))
    file1="${variant}Trace_run${i}.tr"
    file2="${variant}Trace_run${j}.tr"
    
    if [ -f "$file1" ] && [ -f "$file2" ]; then
        diff_count=$(diff <(head -100 "$file1") <(head -100 "$file2") | wc -l)
        if [ $diff_count -gt 0 ]; then
            echo "  ✓ Run $i vs Run $j: 不同 ($diff_count 行差异)"
        else
            echo "  ✗ Run $i vs Run $j: 相同 (可能随机种子未生效)"
        fi
    fi
done

echo ""
echo "=========================================="
echo "完成! 现在运行分析:"
echo "  python3 analyser3.py"
echo "=========================================="

