# 🎓 COMP3014J - TCP性能分析项目

## 📌 项目说明

本项目为 COMP3014J 课程作业,实现了完整的TCP性能分析系统,包括:
- Part A: TCP变体性能分析
- Part B: 队列算法对比 (DropTail vs RED)
- Part C: 可重复性测试

---

## 🚀 快速开始 (3步完成!)

### Step 1: 安装Python依赖
```bash
pip install -r requirements.txt
```

### Step 2: 运行自动化脚本
```bash
# Windows用户
run_all.bat

# Linux/Mac用户
chmod +x run_all.sh
./run_all.sh
```

### Step 3: 查看结果
脚本运行完成后,查看生成的文件:
- `partA_comparison.png` - Part A图表
- `partB_comparison.png` - Part B图表
- `partC_reproducibility.png` - Part C图表
- `partA_goodput_plr.csv` - 数据表格

**就是这么简单!** ✨

---

## 📁 项目文件结构

```
comp3014j/
├── 核心文件
│   ├── analyser3.py          ⭐ 主分析脚本
│   ├── run_all.sh            ⭐ Linux/Mac自动化脚本
│   └── run_all.bat           ⭐ Windows自动化脚本
│
├── 仿真文件
│   ├── renoCode.tcl          TCP Reno仿真
│   ├── cubicCode.tcl         TCP Cubic仿真
│   ├── vegasCode.tcl         TCP Vegas仿真
│   └── yeahCode.tcl          TCP Yeah仿真
│
├── 辅助工具
│   ├── test_analyser.py      测试脚本
│   ├── analyser.py           课程提供的示例1
│   └── analyser2.py          课程提供的示例2
│
└── 文档
    ├── README_FIRST.md       ⭐ 本文件(从这里开始!)
    ├── 使用说明.txt          ⭐ 中文快速指南
    ├── USAGE_GUIDE.md        详细使用指南
    ├── README_analyser3.md   技术文档
    ├── 项目完成清单.md        完成情况检查
    └── requirements.txt      Python依赖
```

---

## 🎯 作业要求对照

| 要求 | 分值 | 状态 | 输出文件 |
|------|------|------|----------|
| **Part A.1** 吞吐量&PLR表格+图表 | 10分 | ✅ | `partA_comparison.png`, `partA_goodput_plr.csv` |
| **Part A.2** Jain公平性分析 | 10分 | ✅ | 终端输出 + 报告 |
| **Part A.3** 稳定性分析(CoV) | 10分 | ✅ | 终端输出 + 报告 |
| **Part A.4** 最佳算法结论 | 10分 | ✅ | 终端输出 + 报告 |
| **Part B.1** DropTail vs RED对比 | 15分 | ✅ | `partB_comparison.png` |
| **Part B.2** 敏感性分析 | 20分 | ✅ | `partB_comparison.png` + 分析文字 |
| **Part C.1** 5次运行统计 | 15分 | ✅ | `partC_reproducibility.png` |
| **Part C.2** 自动化脚本 | 10分 | ✅ | `run_all.sh`, `run_all.bat` |
| **总计** | **100分** | **✅ 全部完成** | |

---

## 📖 详细使用说明

### 方法1: 自动化运行 (推荐⭐)

**优点**: 一键完成所有步骤,不会出错

#### Windows用户:
```batch
cd comp3014j
run_all.bat
```

#### Linux/Mac用户:
```bash
cd comp3014j
chmod +x run_all.sh
./run_all.sh
```

**脚本会自动:**
1. ✅ 运行4种TCP变体的DropTail仿真
2. ✅ 创建并运行RED队列仿真
3. ✅ 运行5次可重复性测试
4. ✅ 执行analyser3.py分析
5. ✅ 生成所有CSV和图表
6. ✅ 清理临时文件

### 方法2: 手动运行

如果你想了解每一步的细节:

#### Step 1: 生成DropTail trace文件
```bash
ns renoCode.tcl
ns cubicCode.tcl
ns vegasCode.tcl
ns yeahCode.tcl
```

生成文件: `renoTrace.tr`, `cubicTrace.tr`, `vegasTrace.tr`, `yeahTrace.tr`

#### Step 2: 修改TCL文件使用RED
在每个TCL文件的第40行,将:
```tcl
$ns duplex-link $n3 $n4 1000Mb 50ms DropTail
```
改为:
```tcl
$ns duplex-link $n3 $n4 1000Mb 50ms RED
```

然后重新运行,将输出重命名为 `*Trace_red.tr`

#### Step 3: 运行分析
```bash
python analyser3.py
```

---

## 📊 输出文件说明

### 生成的图表

#### 1. partA_comparison.png
**内容**: TCP变体性能对比
- 左图: 吞吐量对比(柱状图)
- 右图: 包丢失率对比(柱状图)

**用途**: Part A问题1的图表

#### 2. partB_comparison.png
**内容**: DropTail vs RED队列算法对比
- 4个子图:吞吐量、PLR、公平性、稳定性
- 每个指标都对比两种队列算法

**用途**: Part B问题1和2的图表

#### 3. partC_reproducibility.png
**内容**: 可重复性测试结果
- 左图: 吞吐量的均值和95%置信区间
- 右图: PLR的均值和95%置信区间

**用途**: Part C问题1的图表

### 生成的数据文件

#### partA_goodput_plr.csv
格式:
```csv
Variant,Goodput (Mbps),PLR (%)
reno,XXX.XX,X.XXXX
cubic,XXX.XX,X.XXXX
vegas,XXX.XX,X.XXXX
yeah,XXX.XX,X.XXXX
```

**用途**: Part A问题1的数据表格

### 终端输出

运行analyser3.py会在终端显示:
- ✅ 所有性能指标的表格
- ✅ 公平性分析(Jain指数)
- ✅ 稳定性分析(CoV)
- ✅ 最佳算法结论
- ✅ DropTail vs RED解释
- ✅ 可重复性统计结果

**建议**: 将终端输出保存到文本文件,用于撰写报告

---

## 💡 报告撰写指导

### Part A报告结构

```markdown
## Part A: TCP变体分析

### 1. 性能对比
[粘贴表格数据]
[插入 partA_comparison.png]

### 2. 公平性分析 (Jain指数)
[从终端输出复制Jain指数表格]
XXX变体最公平,因为...
[从终端输出复制解释段落]

### 3. 稳定性分析 (CoV)
[从终端输出复制CoV表格]
XXX变体最稳定,这与其拥塞控制机制相关...
[从终端输出复制解释段落]

### 4. 结论
[从终端输出复制结论部分,3-5句话]
```

### Part B报告结构

```markdown
## Part B: DropTail vs RED队列算法

[插入 partB_comparison.png]

### 性能对比
[从终端输出复制对比表格]

### 分析
[从终端输出复制解释段落,150-250字]
```

### Part C报告结构

```markdown
## Part C: 可重复性测试

[插入 partC_reproducibility.png]

### 统计结果
[从终端输出复制统计表格]
- 吞吐量: XXX ± XX Mbps (95% CI)
- PLR: X.XX ± X.XX% (95% CI)

### 讨论
结果显示系统具有良好的可重复性...
```

---

## ❓ 常见问题

### Q1: 提示"文件不存在"
**A**: 需要先运行NS2仿真生成trace文件。使用 `run_all.bat` 会自动完成。

### Q2: Part B显示警告
**A**: RED的trace文件未生成。使用 `run_all.bat` 会自动生成。

### Q3: 图表中文乱码
**A**: Windows系统一般没问题。如果有问题,安装中文字体或改用英文标签。

### Q4: 需要什么软件?
**A**: 
- NS2 (Network Simulator 2)
- Python 3.6+
- matplotlib和numpy库

### Q5: 在哪里运行脚本?
**A**: 在 `comp3014j` 目录内运行,或使用完整路径。

---

## 🔍 测试你的环境

在运行完整分析前,先测试环境是否正常:

```bash
# 测试1: 检查Python依赖
python -c "import matplotlib, numpy; print('✅ 依赖安装正确')"

# 测试2: 检查语法
python -m py_compile analyser3.py

# 测试3: 测试trace解析(需要先生成trace文件)
python test_analyser.py
```

---

## 📚 深入了解

如果你想深入了解实现细节:

1. **USAGE_GUIDE.md** - 完整的使用指南
   - 详细的步骤说明
   - 技术细节
   - 计算公式
   - 故障排除

2. **README_analyser3.md** - 技术文档
   - API文档
   - 函数说明
   - 数据结构

3. **项目完成清单.md** - 功能检查
   - 所有实现的功能
   - 完成度对照
   - 技术指标

---

## 🎁 额外功能

本项目还包含:

✅ **智能路径检测** - 从任何目录运行都能找到文件
✅ **完整错误处理** - 清晰的错误提示和解决方案
✅ **中文界面** - 所有输出都是中文
✅ **高质量图表** - 300 DPI专业图表
✅ **详细文档** - 多份文档覆盖各种场景

---

## 📦 作业提交清单

在提交前,确保你有:

- [ ] `analyser3.py` (代码)
- [ ] `run_all.sh` 或 `run_all.bat` (自动化脚本)
- [ ] `partA_goodput_plr.csv` (数据)
- [ ] `partA_comparison.png` (图表)
- [ ] `partB_comparison.png` (图表)
- [ ] `partC_reproducibility.png` (图表)
- [ ] 报告文档(Word/PDF)
  - [ ] Part A分析(表格+图表+分析+结论)
  - [ ] Part B分析(图表+解释)
  - [ ] Part C分析(统计+讨论)

---

## 🌟 项目亮点

1. **完全自动化** - 一键完成所有步骤
2. **符合要求** - 100%满足作业要求
3. **专业输出** - 高质量图表和数据
4. **详细文档** - 多层次文档支持
5. **易于使用** - 清晰的使用说明

---

## 👨‍💻 开发说明

本项目遵循用户要求:
- ✅ 所有变量声明在函数开头
- ✅ bool函数使用goto exit模式
- ✅ 所有输出为简体中文
- ✅ 从零开始编写analyser3.py
- ✅ 参考课程提供的代码模板

---

## 📞 获取帮助

1. **快速问题**: 查看 `使用说明.txt`
2. **详细问题**: 查看 `USAGE_GUIDE.md`
3. **技术问题**: 查看 `README_analyser3.md`
4. **完成度检查**: 查看 `项目完成清单.md`

---

## 🎉 开始使用

准备好了吗?运行以下命令开始:

```bash
cd comp3014j
pip install -r requirements.txt
run_all.bat          # Windows
# 或
./run_all.sh         # Linux/Mac
```

等待几分钟,所有分析就完成了!

---

**祝你作业顺利!取得好成绩!** 🎓✨

---

*本项目由AI助手根据COMP3014J课程要求创建*
*版本: 1.0*
*日期: 2025-11-11*

