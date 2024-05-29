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

# 执行 npm install
Write-Host "正在安装 npm 依赖..."
npm install
if ($?) {
    Write-Host "npm 依赖安装成功。"
} else {
    Write-Host "npm 依赖安装失败。"
    Read-Host -Prompt "按 Enter 键退出..."
    exit
}

# 启动 Node.js 应用
Write-Host "正在启动 Node.js 应用..."
node app.js
if ($?) {
    Write-Host "Node.js 应用启动成功。"
} else {
    Write-Host "Node.js 应用启动失败。"
}

# 保持窗口打开
Write-Host "按任意键关闭窗口..."
pause
