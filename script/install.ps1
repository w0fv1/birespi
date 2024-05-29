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

# 创建Python虚拟环境
Write-Host "正在创建Python虚拟环境..."
python -m venv venv
if ($?) {
    Write-Host "虚拟环境创建成功。"
} else {
    Write-Host "虚拟环境创建失败，请检查Python是否正确安装。"
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# 激活虚拟环境
Write-Host "正在激活虚拟环境..."
. .\venv\Scripts\Activate.ps1
if ($?) {
    Write-Host "虚拟环境激活成功。"
} else {
    Write-Host "虚拟环境激活失败。"
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# 安装依赖
Write-Host "正在安装依赖..."
pip install -r requirements.txt
if ($?) {
    Write-Host "依赖安装成功。"
} else {
    Write-Host "依赖安装失败，请检查requirements.txt文件是否存在。"
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# 等待用户输入退出
# 保持窗口打开
Write-Host "按任意键关闭窗口..."
pause
