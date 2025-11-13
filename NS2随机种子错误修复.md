# NS2 随机种子错误修复

## 🐛 错误信息

```
invalid command name "abort"
    while executing
"abort "cannot update defaultRNG once assigned""
    (write trace on "defaultRNG")
    invoked from within
"set defaultRNG $rng"
```

## 🔍 原因

NS2 不允许重新设置 `defaultRNG`,它在 Simulator 创建时已经被初始化。

## ✅ 解决方案

**移除** `set defaultRNG $rng` 这一行。

### 修复前 (错误):
```tcl
set ns [new Simulator]

set rng [new RNG]
$rng seed 18134
set defaultRNG $rng        # ← 这行会导致错误!
```

### 修复后 (正确):
```tcl
set ns [new Simulator]

set rng [new RNG]
$rng seed 18134            # 只设置rng,不设置defaultRNG
set rng2 [new RNG]
$rng2 seed 18245
ns-random 18134
```

## 🎲 正确的随机种子设置方法

对于NS2,使用以下方法设置随机性:

```tcl
# 方法1: 创建RNG对象
set rng [new RNG]
$rng seed 12345

# 方法2: 创建多个RNG
set rng2 [new RNG]
$rng2 seed 67890

# 方法3: ns-random命令
ns-random 12345
```

**不要尝试修改 defaultRNG!**

## 📝 已修复的文件

所有脚本已修复:
- ✅ `run_all.sh`
- ✅ `generate_runs.py`
- ✅ `quick_generate_runs.sh`

## 🚀 现在可以运行了

```bash
cd ~/COMP3014J_Lab

# 清理旧文件
rm -f renoTrace_run*.tr reno_run*.nam

# 重新运行
./run_all.sh
```

## 🎯 预期结果

现在应该能成功生成5个不同的trace文件:

```
运行 reno - 第 1 次...
  随机种子: 19134
  FTP1启动时间抖动: 0.13831 秒
  FTP2启动时间抖动: 0.394038 秒
  输出文件: renoTrace_run1.tr
  ✓ 完成! 文件大小: 245K

运行 reno - 第 2 次...
  随机种子: 31479
  FTP1启动时间抖动: 0.177928 秒
  FTP2启动时间抖动: 0.311036 秒
  输出文件: renoTrace_run2.tr
  ✓ 完成! 文件大小: 248K
...
```

## ✅ 验证修复

```bash
# 运行脚本
./run_all.sh

# 检查是否生成了5个文件
ls -lh renoTrace_run*.tr

# 应该看到5个文件,大小不同
```

修复完成! 🎉

