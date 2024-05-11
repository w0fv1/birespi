#!/bin/bash

# 设置虚拟环境的路径
venvPath="./venv/bin/activate"

# 检查虚拟环境是否存在
if [ ! -f "$venvPath" ]; then
    venvPath="./birespi/bin/activate"
    
    if [ ! -f "$venvPath" ]; then
        echo "虚拟环境不存在，请先创建虚拟环境。"
        read -p "按 Enter 键退出..." 
        exit
    fi
fi

# 激活虚拟环境
source $venvPath

# 运行Python脚本
python main.py

# 等待用户输入，然后退出
read -p "按 Enter 键退出..."
