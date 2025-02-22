@echo off
chcp 1250 >nul
setlocal EnableDelayedExpansion

:: ==============================
:: CONFIGURATION
:: ==============================
set "REPO_URL=https://github.com/TSQSoftware/ArgonCompany.git"
set "FOLDER=ArgonCompany"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip"
set "PYTHON_FOLDER=python_embed"
set "VENV_FOLDER=.venv"
set "ENV_FILE=.env"
set "LICENSE_SERVER=http://dswcsogwc84o4so88osk088c.57.129.132.234.sslip.io/api/v1/license/activate"
set "APP_PORT=8000"
set "GIT_INSTALLER_URL=https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/Git-2.45.1-64-bit.exe"

:: ==============================
:: ELEVATE TO ADMIN IF NEEDED
:: ==============================
NET FILE >nul 2>&1
if %errorlevel% equ 0 (set "ADMIN=1") else (set "ADMIN=0")

if %ADMIN% equ 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:INSTALL_GIT
where git >nul 2>nul || (
    echo Installing Git...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GIT_INSTALLER_URL%' -OutFile 'git_installer.exe'"
    if exist "git_installer.exe" (
        start /wait "" "git_installer.exe" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS
        timeout /t 5 >nul
        del "git_installer.exe"
    )
    set "PATH=%PATH%;C:\Program Files\Git\cmd"
)


:: ==============================
:: MAIN SCRIPT
:: ==============================
pushd "%~dp0"

if exist "%FOLDER%\%ENV_FILE%" (
    echo [INFO] Existing installation detected, skipping license check...
    set SKIP_LICENSE=1
) else (
    set SKIP_LICENSE=0
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%A in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%A
    echo [INFO] Python detected at %PYTHON_EXE%
) else (
    echo [INFO] Python not found. Using embedded Python...
    if not exist "%PYTHON_FOLDER%" (
        mkdir "%PYTHON_FOLDER%"
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python.zip'"
        powershell -Command "Expand-Archive -Path 'python.zip' -DestinationPath '%PYTHON_FOLDER%'"
        del python.zip
        copy "%PYTHON_FOLDER%\python._pth" "%PYTHON_FOLDER%\python._pth.bak"
        echo.>"%PYTHON_FOLDER%\python._pth"
        (echo import site >> "%PYTHON_FOLDER%\python._pth")
    )
    set "PYTHON_EXE=%CD%\%PYTHON_FOLDER%\python.exe"

    if not exist "%PYTHON_FOLDER%\Scripts\pip.exe" (
        echo [INFO] Installing pip...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
        "%PYTHON_EXE%" get-pip.py
        del get-pip.py
    )
)

if exist "%FOLDER%" (
    echo [INFO] Updating existing repository...
    cd "%FOLDER%"
    git pull
) else (
    echo [INFO] Cloning repository...
    git clone "%REPO_URL%" "%FOLDER%"
    cd "%FOLDER%"
)

if exist "%PYTHON_EXE%" (
    echo [INFO] Creating virtual environment...
    "%PYTHON_EXE%" -m venv "%VENV_FOLDER%"
    call "%VENV_FOLDER%\Scripts\activate"
) else (
    echo [ERROR] Python installation failed.
    exit /b 1
)

echo [INFO] Installing dependencies...
pip install -r requirements.txt

:LICENSE_LOOP
if %SKIP_LICENSE%==0 (
    :COMPANY_INPUT
    set /p "COMPANY_NAME=Enter company name: "
    if "!COMPANY_NAME!"=="" (
        echo [ERROR] Company name cannot be empty.
        goto COMPANY_INPUT
    )

    :SERVER_IP_INPUT
    set /p "SERVER_IP=Enter server IP address: "
    if "!SERVER_IP!"=="" (
        echo [ERROR] Server IP cannot be empty.
        goto SERVER_IP_INPUT
    )

    :LICENSE_KEY_INPUT
    set /p "LICENSE_KEY=Enter license key: "
    if "!LICENSE_KEY!"=="" (
        echo [ERROR] License key cannot be empty.
        goto LICENSE_KEY_INPUT
    )

    echo Validating license...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%LICENSE_SERVER%?company_name=!COMPANY_NAME!&activation_key=!LICENSE_KEY!&ipv4_address=!SERVER_IP!' -OutFile 'license.json'"

    if not exist license.json (
        echo [ERROR] License response is missing!
        goto LICENSE_LOOP
    )

    for /f "tokens=*" %%A in ('findstr /i "error" license.json') do (
        echo [ERROR] License error found: %%A
        echo [ERROR] License validation failed. Exiting...
        goto LICENSE_LOOP
    )

    echo License validated successfully!

    echo COMPANY_NAME=!COMPANY_NAME! >> "%ENV_FILE%"
    echo SERVER_IP=!SERVER_IP! >> "%ENV_FILE%"
    echo LICENSE_KEY=!LICENSE_KEY! >> "%ENV_FILE%"

    set CHARS=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%%^&*()_+-=[]{}|;:,.<>?/~
    set "SECRET_KEY="
    for /l %%i in (1,1,128) do (
        set /a "RAND_INDEX=!random! %% 94"
        for /f "delims=" %%A in ("!RAND_INDEX!") do (
            set "CHAR=!CHARS:~%%A,1!"
            set "SECRET_KEY=!SECRET_KEY!!CHAR!"
        )
    )

    echo SECRET_KEY=!SECRET_KEY! >> "%ENV_FILE%"
    echo DEBUG=False >> "%ENV_FILE%"
    echo !SERVER_IP! > address.txt
    if not "!APP_PORT!"=="" echo PORT=!APP_PORT! >> "%ENV_FILE%"
)


:: ======== MIGRATIONS ========
echo [%time%] Running migrations | tee -a "%LOG_FILE%"
python manage.py migrate >> "%LOG_FILE%" 2>&1 || (
    echo [ERROR] Database migrations failed | tee -a "%LOG_FILE%"
    echo [DEBUG] Check database settings in settings.py | tee -a "%LOG_FILE%"
    exit /b 1
)

:: ======== FINAL STARTUP ========
echo [%time%] Starting application | tee -a "%LOG_FILE%"
python manage.py runserver 0.0.0.0:%APP_PORT% >> "%LOG_FILE%" 2>&1 || (
    echo [ERROR] Failed to start server | tee -a "%LOG_FILE%"
    echo [DEBUG] Check if port %APP_PORT% is available | tee -a "%LOG_FILE%"
    exit /b 1
)

:: Keep window open after completion
echo [%time%] Installation completed successfully | tee -a "%LOG_FILE%"
echo Press any key to exit...
pause >nul