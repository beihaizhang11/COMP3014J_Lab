# analyser3.py 详细使用指南

## 目录
1. [快速开始](#快速开始)
2. [详细步骤](#详细步骤)
3. [输出说明](#输出说明)
4. [常见问题](#常见问题)
5. [作业提交](#作业提交)

---

## 快速开始

### 最简单的方法 (推荐)

**Windows用户:**
```batch
cd comp3014j
run_all.bat
```

**Linux/Mac用户:**
```bash
cd comp3014j
chmod +x run_all.sh
./run_all.sh
```

这会自动完成所有步骤并生成所有需要的文件。

---

## 详细步骤

### 第一步: 生成 DropTail trace 文件 (Part A)

进入项目目录并运行4个TCP变体的仿真:

```bash
cd "E:\Doc\Study\COMP3014J Performance of Comp Systems\Assignment\Code\comp3014j"

ns renoCode.tcl
ns cubicCode.tcl
ns vegasCode.tcl
ns yeahCode.tcl
```

**生成的文件:**
- `renoTrace.tr`
- `cubicTrace.tr`
- `vegasTrace.tr`
- `yeahTrace.tr`

### 第二步: 修改TCL文件以使用RED队列 (Part B)

#### 方法1: 手动修改

编辑每个TCL文件(`renoCode.tcl`, `cubicCode.tcl`, `vegasCode.tcl`, `yeahCode.tcl`)

找到第40行:
```tcl
$ns duplex-link $n3 $n4 1000Mb 50ms DropTail
```

改为:
```tcl
$ns duplex-link $n3 $n4 1000Mb 50ms RED
```

然后在每个文件的开头修改输出文件名。例如对于`cubicCode.tcl`:
```tcl
# 第18行
set tracefile1 [open cubicTrace_red.tr w]
```

保存并运行:
```bash
ns renoCode.tcl
ns cubicCode.tcl
ns vegasCode.tcl
ns yeahCode.tcl
```

将生成的trace文件重命名为 `*Trace_red.tr`

#### 方法2: 使用PowerShell (Windows)

```powershell
# Reno
(Get-Content renoCode.tcl) -replace 'DropTail', 'RED' -replace 'renoTrace.tr', 'renoTrace_red.tr' | Set-Content renoCode_red.tcl
ns renoCode_red.tcl

# Cubic
(Get-Content cubicCode.tcl) -replace 'DropTail', 'RED' -replace 'cubicTrace.tr', 'cubicTrace_red.tr' | Set-Content cubicCode_red.tcl
ns cubicCode_red.tcl

# Vegas
(Get-Content vegasCode.tcl) -replace 'DropTail', 'RED' -replace 'vegasTrace.tr', 'vegasTrace_red.tr' | Set-Content vegasCode_red.tcl
ns vegasCode_red.tcl

# Yeah
(Get-Content yeahCode.tcl) -replace 'DropTail', 'RED' -replace 'yeahTrace.tr', 'yeahTrace_red.tr' | Set-Content yeahCode_red.tcl
ns yeahCode_red.tcl
```

**生成的文件:**
- `renoTrace_red.tr`
- `cubicTrace_red.tr`
- `vegasTrace_red.tr`
- `yeahTrace_red.tr`

### 第三步: 生成可重复性测试的trace文件 (Part C)

运行cubic变体5次,每次使用不同的随机种子:

```bash
# 运行1
ns cubicCode.tcl
mv cubicTrace.tr cubicTrace_run1.tr

# 运行2
ns cubicCode.tcl
mv cubicTrace.tr cubicTrace_run2.tr

# 运行3
ns cubicCode.tcl
mv cubicTrace.tr cubicTrace_run3.tr

# 运行4
ns cubicCode.tcl
mv cubicTrace.tr cubicTrace_run4.tr

# 运行5
ns cubicCode.tcl
mv cubicTrace.tr cubicTrace_run5.tr
```

**注意:** 为了获得不同的随机结果,你可以在TCL文件中添加随机种子:
```tcl
# 在 "set ns [new Simulator]" 之后添加
global defaultRNG
$defaultRNG seed 12345  # 每次运行使用不同的数字
```

### 第四步: 运行分析脚本

确保所有trace文件都已生成,然后运行:

```bash
python analyser3.py
```

或者从项目根目录运行:

```bash
python comp3014j/analyser3.py
```

---

## 输出说明

### 终端输出

运行`analyser3.py`后,你会在终端看到:

```
============================================================
TCP性能分析器 - analyser3.py
============================================================

============================================================
Part A: TCP变体分析 (DropTail)
============================================================

处理 RENO...
  吞吐量: XXX.XX Mbps
  PLR: X.XXXX%
  公平性: 0.XXXX
  稳定性(CoV): 0.XXXX

处理 CUBIC...
  ...

表格 1: 每个流的总吞吐量和包丢失率
------------------------------------------------------------
变体        吞吐量 (Mbps)          PLR (%)        
------------------------------------------------------------
reno       XXX.XX              X.XXXX         
cubic      XXX.XX              X.XXXX         
vegas      XXX.XX              X.XXXX         
yeah       XXX.XX              X.XXXX         
------------------------------------------------------------

CSV已保存: partA_goodput_plr.csv

图表已保存: partA_comparison.png

表格 2: Jain公平性指数 (最后1/3时间)
------------------------------------------------------------
变体        公平性指数     
------------------------------------------------------------
reno       0.XXXX         
cubic      0.XXXX         
vegas      0.XXXX         
yeah       0.XXXX         
------------------------------------------------------------

最公平的变体: CUBIC (指数: 0.XXXX)

公平性分析:
CUBIC 表现出最高的公平性指数,这意味着两个流之间
的带宽分配最为均衡...

表格 3: 吞吐量稳定性 (变异系数 CoV)
------------------------------------------------------------
变体        CoV            
------------------------------------------------------------
reno       0.XXXX         
cubic      0.XXXX         
vegas      0.XXXX         
yeah       0.XXXX         
------------------------------------------------------------

最稳定的变体: VEGAS (CoV: 0.XXXX)

稳定性分析:
VEGAS 具有最低的变异系数,表明其吞吐量最稳定...

============================================================
Part A 总结
============================================================

在当前设置下,CUBIC 算法表现最佳。
主要原因包括:
1. 吞吐量最高 (XXX.XX Mbps)
2. 包丢失率为 X.XXXX%
3. 公平性指数为 0.XXXX
4. 稳定性(CoV)为 0.XXXX

综合考虑吞吐量、公平性和稳定性,CUBIC 在这个
特定拓扑和流量模式下提供了最优的性能平衡。


============================================================
Part B: DropTail vs RED 队列算法比较
============================================================

[类似的分析输出...]


============================================================
Part C: 可重复性测试
============================================================

[统计分析输出...]

============================================================
分析完成!
============================================================

生成的文件:
  - partA_goodput_plr.csv
  - partA_comparison.png
  - partB_comparison.png
  - partC_reproducibility.png
============================================================
```

### 生成的文件

#### 1. CSV文件
- **partA_goodput_plr.csv**
  - 格式: Variant, Goodput (Mbps), PLR (%)
  - 包含4个TCP变体的数据

#### 2. 图表文件

##### partA_comparison.png
两个子图:
- 左图: 吞吐量对比 (柱状图)
- 右图: PLR对比 (柱状图)

##### partB_comparison.png
四个子图 (2x2):
- 左上: 吞吐量对比 (DropTail vs RED)
- 右上: PLR对比
- 左下: 公平性对比
- 右下: 稳定性(CoV)对比

##### partC_reproducibility.png
两个子图:
- 左图: 吞吐量的均值和95%置信区间
- 右图: PLR的均值和95%置信区间

---

## 常见问题

### Q1: 运行时提示"警告: 文件不存在"

**A:** 确保你已经运行了NS2仿真生成trace文件:
```bash
ns renoCode.tcl
ns cubicCode.tcl
ns vegasCode.tcl
ns yeahCode.tcl
```

### Q2: Part B显示"未找到RED trace文件"

**A:** 你需要:
1. 修改TCL文件将DropTail改为RED
2. 重新运行仿真
3. 将生成的文件命名为 `*Trace_red.tr`

或者直接运行自动化脚本 `run_all.bat` 或 `run_all.sh`

### Q3: Part C显示"未找到所有运行的trace文件"

**A:** Part C需要5次独立运行的结果:
```bash
cubicTrace_run1.tr
cubicTrace_run2.tr
cubicTrace_run3.tr
cubicTrace_run4.tr
cubicTrace_run5.tr
```

使用自动化脚本可以自动生成这些文件。

### Q4: 图表显示为空或数据为0

**A:** 可能原因:
1. trace文件格式不正确
2. 仿真时间太短(应该是100秒)
3. 流量未正确启动

运行测试脚本检查:
```bash
python test_analyser.py
```

### Q5: 在哪个目录运行脚本?

**A:** 可以在两个位置运行:
```bash
# 方法1: 在comp3014j目录内
cd comp3014j
python analyser3.py

# 方法2: 在项目根目录
python comp3014j/analyser3.py
```

脚本会自动检测路径并找到trace文件。

### Q6: matplotlib显示中文乱码

**A:** 修改analyser3.py,添加字体设置:
```python
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Windows
# 或
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac
```

### Q7: 需要安装哪些Python包?

**A:**
```bash
pip install matplotlib numpy
```

或使用requirements.txt:
```bash
pip install -r requirements.txt
```

---

## 作业提交

### 必需文件清单

- [ ] **代码文件**
  - [ ] `analyser3.py` - 主分析脚本
  - [ ] `run_all.sh` 或 `run_all.bat` - 自动化脚本

- [ ] **数据文件**
  - [ ] `partA_goodput_plr.csv` - Part A数据表格

- [ ] **图表文件**
  - [ ] `partA_comparison.png` - Part A对比图
  - [ ] `partB_comparison.png` - Part B对比图
  - [ ] `partC_reproducibility.png` - Part C可重复性图

- [ ] **报告文档** (Word/PDF)
  - [ ] Part A: 表格 + 图表 + 公平性分析 + 稳定性分析 + 结论
  - [ ] Part B: 对比图 + 解释(150-250字)
  - [ ] Part C: 统计结果 + 可重复性讨论

### 报告撰写指导

#### Part A 结构

```markdown
## Part A: TCP变体分析

### 1. 性能对比
[插入 partA_comparison.png]
[插入表格数据]

### 2. 公平性分析
Jain公平性指数结果显示...
[一段话解释最公平的变体及其原因]

### 3. 稳定性分析
变异系数(CoV)结果显示...
[一段话解释最稳定的变体与其拥塞控制机制的关系]

### 4. 结论
综合评估,XXX算法表现最佳,因为...
[3-5句话总结]
```

#### Part B 结构

```markdown
## Part B: DropTail vs RED

[插入 partB_comparison.png]

### 分析
DropTail和RED在性能上存在显著差异...
[150-250字解释差异原因]

### 敏感性分析
[如果做了不同容量的测试,在这里说明]
```

#### Part C 结构

```markdown
## Part C: 可重复性测试

[插入 partC_reproducibility.png]

### 统计结果
- 吞吐量: XXX ± XX Mbps (95% CI)
- PLR: X.XX ± X.XX % (95% CI)

### 讨论
通过5次独立运行,结果显示...
[讨论结果的可靠性和变异性]
```

---

## 技术细节

### Trace文件格式

NS2生成的trace文件格式:
```
事件 时间 源节点 目标节点 包类型 包大小 ... 流ID ...
+    1.0  0      1       tcp    1000   ... 0.0.0 ...
r    1.1  0      1       tcp    1000   ... 0.0.0 ...
d    2.5  3      4       tcp    1000   ... 1.0.1 ...
```

- `+`: 包进入队列
- `r`: 包被接收
- `d`: 包被丢弃

### 计算公式

**吞吐量 (Goodput):**
```
Goodput = (总接收字节数 × 8) / (仿真时间 × 10^6) Mbps
```

**包丢失率 (PLR):**
```
PLR = (丢包数 / 发送包数) × 100%
```

**Jain公平性指数:**
```
J = (Σxi)² / (n × Σxi²)
```

**变异系数 (CoV):**
```
CoV = σ / μ
```

---

## 额外提示

1. **运行顺序很重要**: 先生成所有trace文件,再运行分析脚本
2. **文件命名要正确**: RED的文件必须是 `*Trace_red.tr`
3. **检查trace文件大小**: 如果文件太小(<100KB),可能仿真有问题
4. **保存原始输出**: 终端输出包含重要的分析文本
5. **备份文件**: 在运行新仿真前备份旧的trace文件

---

**祝你完成出色的作业!** 🎓📊

