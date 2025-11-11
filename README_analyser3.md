# TCP性能分析器使用说明

## 文件说明

### 核心文件
- `analyser3.py` - 主分析脚本,用于完成Part A、B、C的所有分析
- `run_all.sh` - Linux/Mac自动化运行脚本
- `run_all.bat` - Windows自动化运行脚本

### TCL仿真文件
- `renoCode.tcl` - TCP Reno变体仿真
- `cubicCode.tcl` - TCP Cubic变体仿真
- `vegasCode.tcl` - TCP Vegas变体仿真
- `yeahCode.tcl` - TCP Yeah变体仿真

## 快速开始

### 方法1: 使用自动化脚本(推荐)

#### Linux/Mac用户:
```bash
cd comp3014j
chmod +x run_all.sh
./run_all.sh
```

#### Windows用户:
```batch
cd comp3014j
run_all.bat
```

自动化脚本会:
1. 运行所有DropTail仿真 (Part A)
2. 创建并运行所有RED仿真 (Part B)
3. 运行5次可重复性测试 (Part C)
4. 执行所有分析脚本
5. 生成CSV和图表文件
6. 清理临时文件

### 方法2: 手动运行

#### Step 1: 运行DropTail仿真
```bash
ns renoCode.tcl
ns cubicCode.tcl
ns vegasCode.tcl
ns yeahCode.tcl
```

#### Step 2: 修改TCL文件以使用RED队列
在每个TCL文件中,将第40行的 `DropTail` 改为 `RED`:
```tcl
# 修改前:
$ns duplex-link $n3 $n4 1000Mb 50ms DropTail

# 修改后:
$ns duplex-link $n3 $n4 1000Mb 50ms RED
```

然后重新运行仿真,将输出文件重命名为 `*Trace_red.tr`

#### Step 3: 运行多次仿真(可重复性测试)
修改TCL文件添加不同的随机种子,运行5次,保存为 `cubicTrace_run1.tr` 到 `cubicTrace_run5.tr`

#### Step 4: 运行分析
```bash
python3 analyser3.py
```

## 输出文件说明

### CSV文件
- `partA_goodput_plr.csv` - Part A的吞吐量和包丢失率数据

### 图表文件
- `partA_comparison.png` - Part A的TCP变体对比图(吞吐量和PLR)
- `partB_comparison.png` - Part B的DropTail vs RED对比图
- `partC_reproducibility.png` - Part C的可重复性测试结果(均值±95%CI)

### Trace文件
- `*Trace.tr` - DropTail队列的trace文件
- `*Trace_red.tr` - RED队列的trace文件
- `*Trace_run*.tr` - 可重复性测试的trace文件

## Part A: TCP变体分析

### 分析内容
1. **吞吐量和PLR对比** - 4种TCP变体的性能表格和对比图
2. **公平性分析** - Jain公平性指数计算(基于最后1/3时间)
3. **稳定性分析** - 变异系数(CoV)计算
4. **最佳算法结论** - 综合评估

### 关键指标
- **Goodput (Mbps)**: 有效吞吐量
- **PLR (%)**: 包丢失率
- **Fairness Index**: Jain公平性指数 (0-1, 越接近1越公平)
- **CoV**: 变异系数 (越小越稳定)

## Part B: DropTail vs RED

### 分析内容
1. **性能对比** - 吞吐量、PLR、公平性、稳定性的对比
2. **队列算法影响分析** - 解释两种队列算法的差异

### DropTail特点
- 被动丢包:仅在队列满时丢包
- 可能导致全局同步
- 简单但可能产生突发丢包

### RED特点
- 主动丢包:队列未满时就开始随机丢包
- 减少全局同步
- 更平滑的丢包模式

## Part C: 可重复性测试

### 分析内容
1. **多次运行统计** - 5次运行的均值和标准差
2. **95%置信区间** - 结果的可靠性评估

### 方法
- 使用不同随机种子运行5次
- 计算均值、标准差、95%置信区间
- 绘制误差条图

## Jain公平性指数公式

```
J(x1, x2, ..., xn) = (Σxi)² / (n * Σxi²)
```

其中:
- xi: 流i的吞吐量
- n: 流的总数
- J: 公平性指数 (0-1)

## 变异系数(CoV)公式

```
CoV = σ / μ
```

其中:
- σ: 标准差
- μ: 均值
- CoV越小表示越稳定

## 依赖项

### 必需软件
- NS2 (Network Simulator 2)
- Python 3.6+
- matplotlib
- numpy

### 安装Python依赖
```bash
pip install matplotlib numpy
```

## 故障排除

### 问题1: trace文件未生成
**解决**: 确保NS2正确安装,并且TCL文件中的路径正确

### 问题2: Python脚本报错"文件不存在"
**解决**: 先运行仿真生成trace文件,再运行分析脚本

### 问题3: RED仿真结果异常
**解决**: 检查TCL文件中是否正确将所有DropTail改为RED

### 问题4: 图表无法显示
**解决**: 
- 确保matplotlib已安装
- 如果在远程服务器上,可能需要配置显示环境
- 图表会自动保存为PNG文件,可以直接查看文件

## 作业提交清单

### 必需文件
- [ ] `analyser3.py` - 分析脚本
- [ ] `run_all.sh` 或 `run_all.bat` - 自动化脚本
- [ ] `partA_goodput_plr.csv` - Part A数据
- [ ] `partA_comparison.png` - Part A图表
- [ ] `partB_comparison.png` - Part B图表
- [ ] `partC_reproducibility.png` - Part C图表

### 报告内容
- [ ] Part A表格和图表
- [ ] Part A公平性分析(段落说明)
- [ ] Part A稳定性分析(段落说明)
- [ ] Part A结论(3-5句话)
- [ ] Part B对比图表
- [ ] Part B解释(150-250字)
- [ ] Part C统计结果(均值±95%CI)
- [ ] Part C可重复性讨论

## 联系与支持

如有问题,请参考:
1. NS2官方文档
2. Python matplotlib文档
3. 课程提供的示例代码

---

**祝你作业顺利!** 🎓

