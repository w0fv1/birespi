@echo off

:: 获取脚本所在目录
set scriptDir=%~dp0
cd /d %scriptDir%

:: 确认管理员权限
echo Checking for administrative privileges...
>nul 2>&1 "%SystemRoot%\system32\cacls.exe" "%SystemRoot%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto :RunAsAdmin
) else (
    goto :GotPrivileges
)

:RunAsAdmin
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/C %~s0 %*", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /b

:GotPrivileges
    echo Administrative privileges confirmed.

:: 执行 npm install
echo 正在安装 npm 依赖...
call npm install
if %errorlevel% equ 0 (
    echo npm 依赖安装成功。
) else (
    echo npm 依赖安装失败。
    pause
    exit /b
)

:: 启动 Node.js 应用
echo 正在启动 Node.js 应用...
node app.js
if %errorlevel% equ 0 (
    echo Node.js 应用启动成功。
) else (
    echo Node.js 应用启动失败。
)

:: 保持窗口打开
echo 按任意键关闭窗口...
pause
