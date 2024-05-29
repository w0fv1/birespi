@echo off

:: 获取脚本所在目录
set scriptDir=%~dp0
cd /d %scriptDir%
cd ..

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

:: 创建Python虚拟环境
echo 正在创建Python虚拟环境...
python -m venv venv
if %errorlevel% equ 0 (
    echo 虚拟环境创建成功。
) else (
    echo 虚拟环境创建失败，请检查Python是否正确安装或权限是否足够。
    pause
    exit /b
)

:: 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% equ 0 (
    echo 虚拟环境激活成功。
) else (
    echo 虚拟环境激活失败。
    pause
    exit /b
)

:: 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo 依赖安装成功。
) else (
    echo 依赖安装失败，请检查requirements.txt文件是否存在。
    pause
    exit /b
)

:: 等待用户输入退出
echo 操作完成，请按任意键退出
pause
