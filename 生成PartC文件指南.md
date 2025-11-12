# 生成 Part C 文件指南

## 问题: "警告: 未找到所有运行的trace文件"

这说明5次运行的trace文件还没有生成。

## 🚀 解决方案

### 方法1: 使用快速脚本 (最简单)

```bash
cd ~/COMP3014J_Lab

# 给予执行权限
chmod +x quick_generate_runs.sh

# 运行脚本
./quick_generate_runs.sh
```

这个脚本会:
- 自动生成5次Reno运行
- 显示详细的配置信息
- 验证文件是否生成
- 保留第一个TCL文件供检查

### 方法2: 使用Python脚本

```bash
cd ~/COMP3014J_Lab
python3 generate_runs.py
```

### 方法3: 使用完整脚本 (需要运行Part A和B)

```bash
cd ~/COMP3014J_Lab
./run_all.sh
```

## 📁 需要生成的文件

```
renoTrace_run1.tr    # 第1次运行
renoTrace_run2.tr    # 第2次运行
renoTrace_run3.tr    # 第3次运行
renoTrace_run4.tr    # 第4次运行
renoTrace_run5.tr    # 第5次运行
```

## 🔍 验证文件已生成

### 检查文件是否存在
```bash
ls -lh renoTrace_run*.tr
```

应该看到5个文件:
```
-rw-r--r-- 1 user user 242K renoTrace_run1.tr
-rw-r--r-- 1 user user 248K renoTrace_run2.tr
-rw-r--r-- 1 user user 243K renoTrace_run3.tr
-rw-r--r-- 1 user user 247K renoTrace_run4.tr
-rw-r--r-- 1 user user 244K renoTrace_run5.tr
```

### 检查文件大小是否不同
```bash
# 显示每个文件的大小(字节)
for i in {1..5}; do
    size=$(stat -c%s renoTrace_run$i.tr 2>/dev/null || stat -f%z renoTrace_run$i.tr 2>/dev/null)
    echo "Run $i: $size bytes"
done
```

**如果所有文件大小完全相同** → 随机性没有生效
**如果文件大小不同** → ✅ 正确!

## 🎯 生成后运行分析

```bash
cd ~/COMP3014J_Lab

# 运行分析脚本
python3 analyser3.py
```

应该看到:
```
Part C: 可重复性测试
============================================================

说明: Part C需要运行多次仿真(不同随机种子)
...

处理运行 1/5...
处理运行 2/5...
处理运行 3/5...
处理运行 4/5...
处理运行 5/5...

RENO 变体 - 5次运行的统计结果:
------------------------------------------------------------
指标                  均值            标准差          95% CI         
------------------------------------------------------------
吞吐量 (Mbps)         240.32          5.45           ±10.68         
PLR (%)               0.1234          0.0089          ±0.0174        
------------------------------------------------------------

图表已保存: partC_reproducibility.png
```

## 📊 查看结果

```bash
# 打开图表
eog partC_reproducibility.png &

# 或
xdg-open partC_reproducibility.png
```

## ❓ 常见问题

### Q1: NS2命令找不到
```bash
# 检查NS2
which ns

# 如果没有,安装
sudo apt-get install ns2
```

### Q2: 权限错误
```bash
chmod +x quick_generate_runs.sh
chmod +x generate_runs.py
```

### Q3: renoCode.tcl不存在
```bash
# 检查当前目录
pwd

# 应该在
cd ~/COMP3014J_Lab

# 或
cd /path/to/comp3014j
```

### Q4: 脚本运行但没生成文件
```bash
# 检查NS2是否能运行
ns renoCode.tcl

# 查看错误信息
./quick_generate_runs.sh 2>&1 | tee error.log
```

### Q5: 文件大小完全相同
这说明随机性没生效。检查:

```bash
# 查看生成的TCL文件
cat renoCode_run1.tcl | grep -A 12 "Random seed"

# 应该看到:
# set rng [new RNG]
# $rng seed 18134
# set defaultRNG $rng
```

## 🔧 手动生成 (如果脚本都不工作)

### 手动创建每个运行:

#### Run 1:
```bash
# 编辑renoCode.tcl
cp renoCode.tcl renoCode_run1.tcl

# 在 "set ns [new Simulator]" 后添加:
# set rng [new RNG]
# $rng seed 18134
# set defaultRNG $rng
# ns-random 18134

# 修改输出文件名
# set tracefile1 [open renoTrace_run1.tr w]
# set namfile [open reno_run1.nam w]

# 修改启动时间
# $ns at 0.234 "$myftp1 start"
# $ns at 0.456 "$myftp2 start"

# 运行
ns renoCode_run1.tcl
```

重复Run 2-5,每次使用不同的:
- 随机种子: 30479, 42824, 55169, 67514
- 启动时间: 不同的0-0.5秒值

## 📝 完整流程

```bash
# 1. 进入目录
cd ~/COMP3014J_Lab

# 2. 清理旧文件
rm -f renoTrace_run*.tr reno_run*.nam

# 3. 生成5次运行
chmod +x quick_generate_runs.sh
./quick_generate_runs.sh

# 4. 验证文件
ls -lh renoTrace_run*.tr

# 5. 运行分析
python3 analyser3.py

# 6. 查看结果
eog partC_reproducibility.png &
```

## ✅ 成功标志

1. ✅ 5个trace文件都存在
2. ✅ 文件大小不同
3. ✅ analyser3.py运行成功
4. ✅ 生成partC_reproducibility.png
5. ✅ 图表显示5个不同高度的柱状图

## 🎉 完成

文件生成后,Part C就完成了!

你可以:
- 将图表插入报告
- 使用终端输出的统计数据
- 解释5次运行的变化原因

