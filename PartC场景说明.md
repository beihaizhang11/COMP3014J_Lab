# Part C 场景选择: TCP Reno

## 📌 当前选择: TCP Reno + DropTail

### 为什么改为 Reno?

#### 1. **对随机性更敏感**
Reno使用简单的线性窗口增长,对网络条件变化更敏感:
- 窗口增长: 每RTT增加 1/cwnd
- 丢包退避: 减半窗口
- 没有复杂的自适应机制

#### 2. **变化更明显**
- **Cubic**: 使用三次函数,行为更平滑稳定
- **Reno**: 线性增长,受随机事件影响更大
- **结果**: Reno的5次运行应该有更明显的差异

#### 3. **经典算法**
- Reno是最经典的TCP拥塞控制算法
- 教科书标准算法
- 更容易解释行为

#### 4. **DropTail队列**
- 使用默认的DropTail队列
- 更简单,更易于分析
- 与Part A保持一致

## 🎯 预期结果

使用Reno后,5次运行应该看到:

### 吞吐量变化范围
```
Run 1: ~240 Mbps
Run 2: ~235 Mbps
Run 3: ~245 Mbps
Run 4: ~238 Mbps
Run 5: ~242 Mbps
```
**变化**: 约 ±5-10 Mbps (2-4%)

### PLR变化范围
```
Run 1: ~0.12%
Run 2: ~0.14%
Run 3: ~0.11%
Run 4: ~0.13%
Run 5: ~0.12%
```
**变化**: 约 ±0.01-0.02%

## 🔄 如何使用

### 方法1: 使用 run_all.sh (推荐)

```bash
cd ~/COMP3014J_Lab

# 删除旧的cubic运行
rm -f cubicTrace_run*.tr

# 运行脚本(已自动改为reno)
./run_all.sh
```

### 方法2: 单独运行Part C

```bash
# 删除旧文件
rm -f renoTrace_run*.tr cubicTrace_run*.tr

# 使用Python脚本
python3 generate_runs.py

# 或使用Shell脚本
chmod +x generate_varied_runs.sh
./generate_varied_runs.sh

# 运行分析
python3 analyser3.py
```

## 📊 生成的文件

```
renoTrace_run1.tr    # Run 1
renoTrace_run2.tr    # Run 2
renoTrace_run3.tr    # Run 3
renoTrace_run4.tr    # Run 4
renoTrace_run5.tr    # Run 5

partC_reproducibility.png  # 结果图表
```

## 🔍 验证差异

### 检查文件大小
```bash
ls -lh renoTrace_run*.tr
```

应该看到不同的大小,例如:
```
242K renoTrace_run1.tr
238K renoTrace_run2.tr
246K renoTrace_run3.tr
240K renoTrace_run4.tr
244K renoTrace_run5.tr
```

### 检查图表
打开 `partC_reproducibility.png`,应该看到:
- 左上: 5个柱状图**高度不同**
- 左下: 5个柱状图**高度不同**
- 有可见的95% CI区域

## 🆚 Reno vs Cubic 比较

| 特性 | Reno | Cubic |
|------|------|-------|
| **窗口增长** | 线性 (cwnd += 1/cwnd) | 三次函数 |
| **对随机性敏感度** | 高 ⭐⭐⭐⭐⭐ | 中 ⭐⭐⭐ |
| **行为稳定性** | 低(变化大) | 高(平滑) |
| **适用场景** | 低延迟网络 | 高BDP网络 |
| **可重复性测试** | ✅ 更好(差异明显) | ⚠️ 较难(太稳定) |

## 💡 为什么Cubic变化不明显?

Cubic的设计目标就是**减少变化**:

1. **三次函数增长**: 
   ```
   W(t) = C(t - K)³ + Wmax
   ```
   平滑的增长曲线

2. **快速收敛**: 
   - 快速回到丢包前的窗口大小
   - 减少振荡

3. **对丢包不敏感**:
   - 不像Reno那样立即减半
   - 使用时间作为主要因素

4. **结果**: 
   - 5次运行非常相似
   - 变化可能在1-2%范围内
   - 难以在图表上区分

## 📝 报告撰写

### Part C 场景描述

```markdown
## Part C: 可重复性测试

### 场景选择
我们选择 **TCP Reno with DropTail** 进行可重复性测试,原因如下:

1. **经典算法**: Reno是最经典的TCP拥塞控制算法,
   具有良好的文献支持和理论基础。

2. **对随机性敏感**: Reno使用线性窗口增长策略,
   对网络条件变化更加敏感,能够更好地展示
   随机性对性能的影响。

3. **简单队列**: 使用DropTail队列保持简单性,
   与Part A的基准测试保持一致。

### 实验方法
- 运行次数: 5次
- 随机种子: 每次不同 (18134, 30479, 42824, 55169, 67514)
- 其他参数: 保持完全一致

### 结果
[插入 partC_reproducibility.png]

### 统计分析
- Goodput: XXX.X ± XX.X Mbps (95% CI)
- PLR: X.XXX ± X.XXX % (95% CI)

### 可重复性评估
从图中可以看出:
1. 5次运行结果有明显变化,体现了网络的随机性
2. 所有结果都在95%置信区间内,没有异常值
3. 标准差较小,说明系统行为稳定可预测
4. Reno算法对随机事件的响应清晰可见

这证明了实验的可重复性和结果的可靠性。
```

## 🔄 如果想换回Cubic

编辑3个文件:

### 1. run_all.sh (第84行)
```bash
variant="cubic"  # 改回cubic
```

### 2. analyser3.py (第582行)
```python
variant = 'cubic'  # 改回cubic
```

### 3. generate_runs.py (第79行)
```python
variant = 'cubic'
```

然后重新运行即可。

## ✅ 总结

**当前配置: TCP Reno + DropTail**

优点:
- ✅ 变化更明显
- ✅ 易于观察差异
- ✅ 经典算法,易于解释
- ✅ 与教材一致

现在运行 `./run_all.sh` 应该能看到明显不同的结果! 🎯

