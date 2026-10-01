@echo off
chcp 65001 >nul
call "D:\PROGRAMM\anaconda3\Scripts\activate.bat" "D:\PROGRAMM\anaconda3\envs\lab1_terminal"
cd /d "%~dp0"
jupyter notebook
pause
