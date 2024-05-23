#!/bin/bash

scriptDir=$(dirname "$0")
cd "$scriptDir"
cd ..
# 创建Python虚拟环境
echo "正在创建Python虚拟环境..."
python -m venv venv
if [ $? -eq 0 ]; then
    echo "虚拟环境创建成功。"
else
    echo "虚拟环境创建失败，请检查Python是否正确安装。"
    exit 1
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo "虚拟环境激活成功。"
else
    echo "虚拟环境激活失败。"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "依赖安装成功。"
else
    echo "依赖安装失败，请检查requirements.txt文件是否存在。"
    exit 1
fi
