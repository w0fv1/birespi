#!/bin/bash
scriptDir=$(dirname "$0")
cd "$scriptDir"
cd ..
# 设置虚拟环境的路径
venvPath="./venv/bin/activate"
echo "检查默认虚拟环境路径..."

# 检查虚拟环境是否存在
if [ ! -f "$venvPath" ]; then
    echo "默认虚拟环境不存在，尝试备用路径..."
    venvPath="./birespi/bin/activate"
    
    if [ ! -f "$venvPath" ]; then
        echo "备用虚拟环境也不存在，请先创建虚拟环境。"
        read -p "按 Enter 键退出..." 
        exit
    else
        echo "备用虚拟环境路径找到。"
    fi
else
    echo "默认虚拟环境路径找到。"
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source $venvPath
echo "虚拟环境激活成功。"

# 运行Python脚本
echo "正在运行 Python 脚本..."
python main.py
echo "Python 脚本执行完成。"

# 等待用户输入，然后退出
read -p "按 Enter 键退出..."
