# 检查管理员权限
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # 不具有管理员权限，则请求管理员权限重新运行脚本
    $script = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)
    Start-Process powershell.exe -ArgumentList "Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File `"$script`"' -Verb RunAs" -Verb RunAs
    exit
}


# 获取脚本所在目录
$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location -Path $scriptDir
Set-Location -Path (Get-Item -Path "..").FullName

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

# 保持窗口打开
Write-Host "按任意键关闭窗口..."
pause
