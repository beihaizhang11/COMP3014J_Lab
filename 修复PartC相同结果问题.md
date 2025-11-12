# 修复 Part C 相同结果问题

## 问题描述

5次运行结果完全相同:
- Goodput: 都是 0.9 Mbps
- PLR: 都是 1.353%

这说明随机种子没有生效,或者运行了相同的配置。

## 原因分析

1. **NS2的随机数生成器未正确配置**
   - 简单的 `seed` 命令可能不够
   - 需要使用 `RNG` 对象

2. **sed命令插入随机种子失败**
   - `sed "11 i\\"` 语法在某些shell中不工作
   - 多行插入可能被截断

3. **文件被跳过**
   - 如果文件已存在,脚本会跳过重新生成

## 解决方案

### 方法1: 使用Python脚本(推荐)

```bash
cd ~/COMP3014J_Lab
python3 generate_runs.py
```

这个脚本会:
1. 为每次运行生成不同的随机种子
2. 添加启动时间的随机抖动
3. 使用正确的NS2 RNG语法
4. 验证生成的文件是否不同

### 方法2: 使用改进的Shell脚本

```bash
cd ~/COMP3014J_Lab
chmod +x generate_varied_runs.sh
./generate_varied_runs.sh
```

### 方法3: 手动修改并运行

对于每次运行,手动编辑 `cubicCode.tcl`:

#### Run 1 - 种子 12345
```tcl
set ns [new Simulator]

# 添加这些行
set rng [new RNG]
$rng seed 12345
set rng2 [new RNG]
$rng2 seed 67890

# 修改输出文件
set tracefile1 [open cubicTrace_run1.tr w]
set namfile [open cubic_run1.nam w]
```

运行: `ns cubicCode.tcl`

#### Run 2 - 种子 23456
重复上述步骤,改变种子值为不同的数字...

## 验证是否成功

### 1. 检查文件大小
```bash
ls -lh cubicTrace_run*.tr
```

应该看到**不同的文件大小**,例如:
```
-rw-r--r-- 1 user user 245K cubicTrace_run1.tr
-rw-r--r-- 1 user user 247K cubicTrace_run2.tr
-rw-r--r-- 1 user user 243K cubicTrace_run3.tr
-rw-r--r-- 1 user user 248K cubicTrace_run4.tr
-rw-r--r-- 1 user user 244K cubicTrace_run5.tr
```

如果所有文件大小**完全相同**,说明问题未解决。

### 2. 快速检查trace内容
```bash
# 检查第一个包的时间戳
for i in {1..5}; do
    echo -n "Run $i: "
    grep "^+ " cubicTrace_run$i.tr | head -1
done
```

应该看到不同的时间戳或序列号。

### 3. 运行分析查看结果
```bash
python3 analyser3.py
```

查看生成的图表,5个柱状图应该有**明显的差异**。

## 为什么需要随机性?

可重复性测试的目的是:
1. **验证系统稳定性** - 多次运行应该有相似但不完全相同的结果
2. **计算统计量** - 均值和置信区间只有在有变化时才有意义
3. **评估可靠性** - 如果每次结果都一样,说明:
   - 要么系统过于确定性(不好)
   - 要么随机性没有生效(错误)

## 期望的结果范围

对于Cubic TCP,5次运行应该有一定变化,例如:

```
Run 1: Goodput = 245.3 Mbps, PLR = 0.123%
Run 2: Goodput = 248.1 Mbps, PLR = 0.119%
Run 3: Goodput = 243.7 Mbps, PLR = 0.127%
Run 4: Goodput = 247.5 Mbps, PLR = 0.121%
Run 5: Goodput = 244.9 Mbps, PLR = 0.125%
```

变化应该在5-10%范围内。

## NS2随机数生成器语法

### 正确的方法:

```tcl
# 创建Simulator后立即添加
set ns [new Simulator]

# 方法1: 使用RNG对象(推荐)
set rng [new RNG]
$rng seed 12345

# 方法2: 设置默认RNG
set defaultRNG [new RNG]
$defaultRNG seed 12345

# 方法3: 使用ns-random命令
ns-random 12345
```

### 错误的方法:

```tcl
# 这个可能不够
seed 12345

# 这个语法不对
$ns seed 12345
```

## 额外的变化方法

除了随机种子,还可以:

### 1. 添加启动时间抖动
```tcl
# 原始
$ns at 0.0 "$myftp1 start"

# 修改为(每次不同)
$ns at 0.05 "$myftp1 start"  # Run 1
$ns at 0.03 "$myftp1 start"  # Run 2
$ns at 0.07 "$myftp1 start"  # Run 3
```

### 2. 修改队列限制
```tcl
$ns queue-limit $n3 $n4 10   # Run 1
$ns queue-limit $n3 $n4 12   # Run 2
$ns queue-limit $n3 $n4 8    # Run 3
```

### 3. 修改包大小
```tcl
$source1 set packet_size_ 1000   # Run 1
$source1 set packet_size_ 1024   # Run 2
$source1 set packet_size_ 976    # Run 3
```

## 故障排除

### 如果Python脚本不工作:

```bash
# 检查NS2是否可用
which ns

# 检查Python版本
python3 --version

# 手动运行一次看错误信息
python3 generate_runs.py
```

### 如果Shell脚本不工作:

```bash
# 给予执行权限
chmod +x generate_varied_runs.sh

# 检查bash版本
bash --version

# 使用bash明确运行
bash generate_varied_runs.sh
```

### 如果仍然相同:

1. **删除所有旧文件**
   ```bash
   rm cubicTrace_run*.tr
   rm cubic_run*.nam
   ```

2. **检查TCL文件是否真的被修改**
   ```bash
   # 运行脚本时不要删除临时TCL文件
   # 检查 cubicCode_run1.tcl 是否有seed命令
   ```

3. **尝试极端不同的配置**
   - 完全不同的拓扑
   - 不同的链路速率
   - 不同的延迟

## 完成后

删除所有旧文件并重新生成:

```bash
cd ~/COMP3014J_Lab

# 清理旧文件
rm -f cubicTrace_run*.tr
rm -f cubic_run*.nam

# 生成新的运行
python3 generate_runs.py

# 验证不同
ls -lh cubicTrace_run*.tr

# 运行分析
python3 analyser3.py

# 查看结果
eog partC_reproducibility.png &
```

现在应该看到5个明显不同的柱状图! ✅

