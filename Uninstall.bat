@echo off
chcp 65001 >nul
title Whisper-Fast-GUI 一键卸载与清理工具

echo =======================================================
echo          Whisper-Fast-GUI 一键卸载与清理工具
echo =======================================================
echo.
echo 请选择要执行的操作：
echo.
echo   [1] 仅清理模型与缓存 (删除 ./models/、配置文件与缓存，保留程序)
echo   [2] 彻底卸载本软件 (清空所有模型与配置，并安全删除本软件目录)
echo   [0] 退出
echo.
set /p choice=请输入选项编号 (0/1/2): 

if "%choice%"=="1" goto clean_cache
if "%choice%"=="2" goto uninstall_all
if "%choice%"=="0" goto end
goto invalid

:clean_cache
echo.
echo [1/3] 正在检查并停止运行中的 Whisper 进程...
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq Whisper*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq Whisper*" >nul 2>&1

echo [2/3] 正在清理已下载的模型文件 (./models/)...
if exist "%~dp0models" (
    rd /s /q "%~dp0models"
    echo      已成功清空本地模型目录: %~dp0models
) else (
    echo      本地模型目录为空，无需清理。
)

echo [3/3] 正在清理配置文件与 Python 缓存...
if exist "%~dp0.whisper_gui_config.json" (
    del /f /q "%~dp0.whisper_gui_config.json"
    echo      已删除本地配置文件: %~dp0.whisper_gui_config.json
)
if exist "%USERPROFILE%\.whisper_gui_config.json" (
    del /f /q "%USERPROFILE%\.whisper_gui_config.json"
    echo      已清理用户主目录残留配置
)
if exist "%~dp0__pycache__" (
    rd /s /q "%~dp0__pycache__"
    echo      已清理 Python 缓存
)

echo.
echo =======================================================
echo [成功] 模型文件与缓存已清理完毕，磁盘空间已释放！
echo =======================================================
echo.
pause
goto end

:uninstall_all
echo.
echo -------------------------------------------------------
echo 警告：彻底卸载将永久删除本软件及其所有已下载模型和配置！
echo -------------------------------------------------------
set /p confirm=确认要彻底删除吗？(输入 Y 确认，其他键取消): 
if /i not "%confirm%"=="Y" (
    echo 已取消卸载操作。
    pause
    goto end
)

echo.
echo [1/3] 正在停止运行中的 Whisper 进程...
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq Whisper*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq Whisper*" >nul 2>&1

echo [2/3] 正在清理全局残留配置文件...
if exist "%USERPROFILE%\.whisper_gui_config.json" (
    del /f /q "%USERPROFILE%\.whisper_gui_config.json"
)

echo [3/3] 正在执行自删除并卸载软件目录...
cd /d "%~dp0.."
start "" cmd /c "(ping 127.0.0.1 -n 3 >nul & rd /s /q \"%~dp0\")"
echo.
echo =======================================================
echo [成功] 软件已完成清理与卸载，本窗口将在 3 秒后自动关闭。
echo =======================================================
timeout /t 3 >nul
exit

:invalid
echo 无效的选项，请重新运行脚本。
pause

:end

