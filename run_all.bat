@echo off
REM 自动化运行脚本 - 执行所有仿真和分析 (Windows版本)

echo ==========================================
echo TCP性能分析 - 自动化运行脚本
echo ==========================================

cd comp3014j 2>nul || cd .

REM Part A: 运行DropTail仿真
echo.
echo Part A: 运行DropTail仿真...
echo ------------------------------------------

echo 运行 Reno...
ns renoCode.tcl

echo 运行 Cubic...
ns cubicCode.tcl

echo 运行 Vegas...
ns vegasCode.tcl

echo 运行 Yeah...
ns yeahCode.tcl

echo DropTail仿真完成!

REM Part B: 创建RED版本的TCL文件并运行
echo.
echo Part B: 准备RED仿真...
echo ------------------------------------------

REM 创建RED版本 - Reno
powershell -Command "(Get-Content renoCode.tcl) -replace 'DropTail', 'RED' -replace 'renoTrace.tr', 'renoTrace_red.tr' -replace 'reno.nam', 'reno_red.nam' | Set-Content renoCode_red.tcl"

REM 创建RED版本 - Cubic
powershell -Command "(Get-Content cubicCode.tcl) -replace 'DropTail', 'RED' -replace 'cubicTrace.tr', 'cubicTrace_red.tr' -replace 'cubic.nam', 'cubic_red.nam' | Set-Content cubicCode_red.tcl"

REM 创建RED版本 - Vegas
powershell -Command "(Get-Content vegasCode.tcl) -replace 'DropTail', 'RED' -replace 'vegasTrace.tr', 'vegasTrace_red.tr' -replace 'vegas.nam', 'vegas_red.nam' | Set-Content vegasCode_red.tcl"

REM 创建RED版本 - Yeah
powershell -Command "(Get-Content yeahCode.tcl) -replace 'DropTail', 'RED' -replace 'yeahTrace.tr', 'yeahTrace_red.tr' -replace 'yeah.nam', 'yeah_red.nam' | Set-Content yeahCode_red.tcl"

echo.
echo 运行RED仿真...
echo 运行 Reno (RED)...
ns renoCode_red.tcl

echo 运行 Cubic (RED)...
ns cubicCode_red.tcl

echo 运行 Vegas (RED)...
ns vegasCode_red.tcl

echo 运行 Yeah (RED)...
ns yeahCode_red.tcl

echo RED仿真完成!

REM Part C: 运行多次仿真(可重复性测试)
echo.
echo Part C: 运行可重复性测试 (5次运行)...
echo ------------------------------------------

set variant=cubic

for %%i in (1 2 3 4 5) do (
    echo 运行 %variant% - 第 %%i 次...
    
    REM 创建临时TCL文件
    powershell -Command "(Get-Content cubicCode.tcl) -replace 'cubicTrace.tr', 'cubicTrace_run%%i.tr' -replace 'cubic.nam', 'cubic_run%%i.nam' | ForEach-Object { if ($_ -match '^set ns') { $_; 'global defaultRNG'; '$defaultRNG seed %%i123' } else { $_ } } | Set-Content cubicCode_run%%i.tcl"
    
    ns cubicCode_run%%i.tcl
    del cubicCode_run%%i.tcl
)

echo 可重复性测试完成!

REM 运行分析脚本
echo.
echo ==========================================
echo 运行分析脚本...
echo ==========================================

echo.
echo 运行 analyser3.py (主分析)...
python analyser3.py

echo.
echo 运行 analyser2.py...
python analyser2.py

echo.
echo 运行 analyser.py...
python analyser.py

REM 清理临时文件
echo.
echo ==========================================
echo 清理临时文件...
echo ==========================================

del *Code_red.tcl

echo.
echo ==========================================
echo 所有任务完成!
echo ==========================================
echo.
echo 生成的文件:
echo   Trace文件:
echo     - *Trace.tr (DropTail)
echo     - *Trace_red.tr (RED)
echo     - *Trace_run*.tr (可重复性测试)
echo.
echo   CSV文件:
echo     - partA_goodput_plr.csv
echo.
echo   图表文件:
echo     - partA_comparison.png
echo     - partB_comparison.png
echo     - partC_reproducibility.png
echo ==========================================

pause

