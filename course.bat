echo ========================================
echo       东北师范大学抢课系统
echo ========================================
echo.
echo 正在启动系统...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未检测到Python环境！
    echo 请先安装Python 3.6或更高版本
    pause
    exit /b 1
)

REM 检查依赖
python -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install flask requests
    if errorlevel 1 (
        echo 错误：依赖安装失败！
        pause
        exit /b 1
    )
    echo 依赖安装完成！
    echo.
)

REM 启动系统
echo 系统启动成功！
echo 浏览器将自动打开...
echo.
echo 如果浏览器未自动打开，请手动访问：
echo http://localhost:5000
echo.
python run.py

pause