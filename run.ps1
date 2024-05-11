# 设置虚拟环境的路径
$venvPath = ".\venv\Scripts\Activate.ps1"
Write-Host "检查虚拟环境路径..."

# 检查虚拟环境是否存在
if (-Not (Test-Path -Path $venvPath)) {
    $venvPath = ".\birespi\Scripts\Activate.ps1"

    if (-Not (Test-Path -Path $venvPath)) {
        Write-Host "虚拟环境不存在，请先创建虚拟环境。"
        Read-Host -Prompt "按 Enter 键退出..."
        exit
    } else {
        Write-Host "找到备用虚拟环境路径。"
    }
} else {
    Write-Host "找到默认虚拟环境路径。"
}

# 激活虚拟环境
Write-Host "正在激活虚拟环境..."
& $venvPath
Write-Host "虚拟环境已激活。"

# 运行Python脚本
Write-Host "正在运行 Python 脚本..."
python main.py
Write-Host "Python 脚本执行完成。"

# 等待用户输入，然后退出
Read-Host -Prompt "按 Enter 键退出..."
