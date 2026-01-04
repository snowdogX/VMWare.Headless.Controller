@echo off
REM VMware 虚拟机管理器 - GUI 启动脚本

echo 正在启动 VMware 虚拟机管理器...
echo.

REM 激活虚拟环境并启动 GUI
call venv\Scripts\activate.bat
python gui.py

pause

