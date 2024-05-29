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

:: 设置虚拟环境路径
set venvPath=.\venv\Scripts\activate.bat
echo 检查虚拟环境路径...

:: 检查虚拟环境是否存在
if not exist "%venvPath%" (
    set venvPath=.\birespi\Scripts\activate.bat

    if not exist "%venvPath%" (
        echo 虚拟环境不存在，请先创建虚拟环境。
        pause
        exit /b
    ) else (
        echo 找到备用虚拟环境路径。
    )
) else (
    echo 找到默认虚拟环境路径。
)

:: 激活虚拟环境
echo 正在激活虚拟环境...
call "%venvPath%"
echo 虚拟环境已激活。

:: 运行Python脚本
echo 正在运行 Python 脚本...
python main.py
echo Python 脚本执行完成。

:: 等待用户输入退出
echo 操作完成，请按任意键退出...
pause
