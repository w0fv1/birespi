# 设置虚拟环境的路径
$venvPath = ".\venv\Scripts\Activate.ps1"

# 检查虚拟环境是否存在
if (-Not (Test-Path -Path $venvPath)) {
    $venvPath = ".\birespi\Scripts\Activate.ps1"

    if (-Not (Test-Path -Path $venvPath)) {
        Write-Host "虚拟环境不存在，请先创建虚拟环境。"
        Read-Host -Prompt "按 Enter 键退出..."
        exit
    }
}

# 激活虚拟环境
& $venvPath

# 运行Python脚本
python main.py

# # 退出虚拟环境
# deactivate

Read-Host -Prompt "按 Enter 键退出..."
