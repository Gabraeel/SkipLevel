@echo off
REM Gera dist\SkipLevel.exe (arquivo unico e portatil). Execute no Windows, dentro desta pasta.
python -m pip install -r requirements.txt || exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SkipLevel --icon assets\icon.ico --add-data "assets;assets" --collect-all customtkinter main.py || exit /b 1
echo.
echo Pronto: dist\SkipLevel.exe
pause
