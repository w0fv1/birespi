# 创建Python虚拟环境
Write-Host "正在创建Python虚拟环境..."
python -m venv venv
if ($?) {
    Write-Host "虚拟环境创建成功。"
} else {
    Write-Host "虚拟环境创建失败，请检查Python是否正确安装。"
    exit
}

# 激活虚拟环境
Write-Host "正在激活虚拟环境..."
. .\venv\Scripts\Activate.ps1
if ($?) {
    Write-Host "虚拟环境激活成功。"
} else {
    Write-Host "虚拟环境激活失败。"
    exit
}

# 安装依赖
Write-Host "正在安装依赖..."
pip install -r requirements.txt
if ($?) {
    Write-Host "依赖安装成功。"
} else {
    Write-Host "依赖安装失败，请检查requirements.txt文件是否存在。"
    exit
}
