# 所有CSV文件总结

## 📊 生成的CSV文件清单

运行 `./run_all.sh` 或 `python3 analyser3.py` 后,会生成:

### ✅ 1. partA_goodput_plr.csv
**Part A: TCP变体性能对比**

```csv
Variant,Goodput (Mbps),PLR (%)
reno,XXX.XX,X.XXXX
cubic,XXX.XX,X.XXXX
vegas,XXX.XX,X.XXXX
yeah,XXX.XX,X.XXXX
```

- **行数**: 5行(1个表头 + 4个变体)
- **列数**: 3列
- **用途**: Part A问题1的数据表格

---

### ✅ 2. partB_droptail_vs_red.csv
**Part B: DropTail vs RED队列对比**

```csv
Variant,Queue,Goodput (Mbps),PLR (%),Fairness Index,Stability (CoV)
reno,DropTail,XXX.XX,X.XXXX,X.XXXX,X.XXXX
reno,RED,XXX.XX,X.XXXX,X.XXXX,X.XXXX
cubic,DropTail,XXX.XX,X.XXXX,X.XXXX,X.XXXX
cubic,RED,XXX.XX,X.XXXX,X.XXXX,X.XXXX
vegas,DropTail,XXX.XX,X.XXXX,X.XXXX,X.XXXX
vegas,RED,XXX.XX,X.XXXX,X.XXXX,X.XXXX
yeah,DropTail,XXX.XX,X.XXXX,X.XXXX,X.XXXX
yeah,RED,XXX.XX,X.XXXX,X.XXXX,X.XXXX
```

- **行数**: 9行(1个表头 + 8个数据行)
- **列数**: 6列
- **用途**: Part B的完整对比数据,包含所有4个性能指标

---

### ✅ 3. partC_reproducibility.csv
**Part C: 可重复性测试数据**

```csv
Run,Goodput (Mbps),PLR (%),Fairness Index,Stability (CoV)
Run 1,0.7116,0.2439,0.7013,1.1831
Run 2,0.7116,0.2439,0.7013,1.1539
Run 3,0.7052,0.2439,0.7056,1.2373
Run 4,0.7099,0.2423,0.7078,1.1198
Run 5,0.7163,0.2423,0.7103,1.1446

Statistic,Goodput (Mbps),PLR (%),Fairness Index,Stability (CoV)
Mean,0.7109,0.2432,0.7052,1.1677
Std Dev,0.0036,0.0008,0.0035,0.0403
95% CI,±0.0070,±0.0015,±0.0070,±0.0789
Min,0.7052,0.2423,0.7013,1.1198
Max,0.7163,0.2439,0.7103,1.2373
Range,0.0111,0.0016,0.0090,0.1176
```

- **行数**: 13行(2个表头 + 5个运行数据 + 6个统计量)
- **列数**: 5列
- **用途**: Part C的完整可重复性分析,包含原始数据和统计分析

---

## 📁 文件位置

所有CSV文件在同一目录:
```bash
~/COMP3014J_Lab/partA_goodput_plr.csv
~/COMP3014J_Lab/partB_droptail_vs_red.csv
~/COMP3014J_Lab/partC_reproducibility.csv
```

## 🔍 查看CSV文件

### 命令行查看:
```bash
# Part A
cat partA_goodput_plr.csv

# Part B
cat partB_droptail_vs_red.csv

# Part C
cat partC_reproducibility.csv

# 格式化显示
column -t -s',' partA_goodput_plr.csv
column -t -s',' partB_droptail_vs_red.csv
column -t -s',' partC_reproducibility.csv
```

### Excel/LibreOffice:
双击文件即可在电子表格程序中打开

## 📝 在报告中使用

### Part A:
```markdown
### 表1: TCP变体性能对比

| TCP变体 | 吞吐量(Mbps) | 包丢失率(%) |
|---------|-------------|-------------|
[从 partA_goodput_plr.csv 复制数据]
```

### Part B:
```markdown
### 表2: DropTail vs RED性能对比

| 变体 | 队列 | 吞吐量 | PLR | 公平性 | 稳定性 |
|------|------|--------|-----|--------|--------|
[从 partB_droptail_vs_red.csv 复制数据]
```

### Part C:
```markdown
### 表3: 5次运行原始数据

| 运行 | 吞吐量 | PLR | 公平性 | CoV |
|------|--------|-----|--------|-----|
[从 partC_reproducibility.csv 复制前5行数据]

### 表4: 统计分析结果

| 统计量 | 吞吐量 | PLR | 公平性 | CoV |
|--------|--------|-----|--------|-----|
[从 partC_reproducibility.csv 复制统计部分]
```

## 🎯 数据精度说明

| 文件 | Goodput精度 | PLR精度 | Fairness精度 | CoV精度 |
|------|-------------|---------|--------------|---------|
| Part A | 2位小数 | 4位小数 | - | - |
| Part B | 2位小数 | 4位小数 | 4位小数 | 4位小数 |
| Part C | 4位小数 | 4位小数 | 4位小数 | 4位小数 |

**Part C使用最高精度**,因为需要展示微小的差异。

## ✅ 检查清单

运行完成后验证:

```bash
# 检查所有CSV是否存在
ls -lh *.csv

# 应该看到3个文件
partA_goodput_plr.csv          (约200 bytes)
partB_droptail_vs_red.csv      (约600 bytes)
partC_reproducibility.csv      (约800 bytes)

# 检查内容
wc -l *.csv

# 应该显示
  5 partA_goodput_plr.csv
  9 partB_droptail_vs_red.csv
 13 partC_reproducibility.csv
```

## 🎓 报告提交清单

- [ ] partA_goodput_plr.csv
- [ ] partB_droptail_vs_red.csv
- [ ] partC_reproducibility.csv
- [ ] partA_comparison.png
- [ ] partB_comparison.png
- [ ] partC_reproducibility.png
- [ ] 报告文档(Word/PDF)

**所有数据文件齐全!** 🎉📊

