@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =============================================
echo 全国艺术培训机构数据采集系统 - 全国版
echo =============================================
echo.
echo 已加载全国34个省级行政区，共344个城市
echo.
python gui_scraper_china.py
pause

