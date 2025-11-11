#!/bin/bash
# 安装Python依赖和系统库

echo "=========================================="
echo "安装依赖 - Ubuntu/Debian系统"
echo "=========================================="

# 检查是否是root用户
if [ "$EUID" -ne 0 ]; then 
    SUDO="sudo"
else
    SUDO=""
fi

echo ""
echo "步骤1: 更新包列表..."
$SUDO apt-get update

echo ""
echo "步骤2: 安装系统级依赖..."
echo "这些是matplotlib和Pillow需要的库"
echo ""

# 安装必需的系统库
$SUDO apt-get install -y \
    python3-pip \
    python3-dev \
    python3-tk \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config

echo ""
echo "步骤3: 升级pip..."
pip3 install --upgrade pip

echo ""
echo "步骤4: 安装Python包..."

# 方法1: 使用系统包管理器(推荐)
echo "尝试使用apt安装..."
$SUDO apt-get install -y \
    python3-matplotlib \
    python3-numpy

if [ $? -eq 0 ]; then
    echo "✓ 使用apt成功安装matplotlib和numpy"
else
    echo "apt安装失败，尝试使用pip..."
    
    # 方法2: 使用pip安装
    pip3 install --user numpy
    pip3 install --user matplotlib
fi

echo ""
echo "=========================================="
echo "测试安装..."
echo "=========================================="

python3 -c "import numpy; print('✓ numpy版本:', numpy.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ numpy安装失败"
else
    echo "✓ numpy安装成功"
fi

python3 -c "import matplotlib; print('✓ matplotlib版本:', matplotlib.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ matplotlib安装失败"
else
    echo "✓ matplotlib安装成功"
fi

echo ""
echo "=========================================="
echo "安装完成!"
echo "=========================================="
echo ""
echo "现在可以运行:"
echo "  python3 analyser3.py"
echo ""

