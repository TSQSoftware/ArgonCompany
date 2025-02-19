@echo off
setlocal EnableDelayedExpansion

:: CONFIGURATION
set REPO_URL=https://github.com/TSQSoftware/ArgonCompany.git
set FOLDER=ArgonCompany
set PYTHON_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip
set PYTHON_FOLDER=python_embed
set VENV_FOLDER=.venv
set ENV_FILE=.env
set LICENSE_SERVER=http://dswcsogwc84o4so88osk088c.57.129.132.234.sslip.io/api/v1/license/activate

:: CHECK IF THE APP WAS INSTALLED BEFORE
if exist "%FOLDER%\%ENV_FILE%" (
    echo [INFO] Previous installation detected, skipping license input...
    set SKIP_LICENSE=1
) else (
    set SKIP_LICENSE=0
)

:: CLONE OR UPDATE REPOSITORY
if exist "%FOLDER%" (
    echo [INFO] Updating existing repository...
    cd %FOLDER%
    git pull
) else (
    echo [INFO] Cloning repository...
    git clone %REPO_URL% %FOLDER%
    cd %FOLDER%
)

:: CHECK IF PYTHON IS INSTALLED
where python >nul 2>nul
if %errorlevel% == 0 (
    echo [INFO] Python found!
    set "USE_SYSTEM_PYTHON=1"
    set "PYTHON_CMD=python"
) else (
    echo [INFO] Python not found, using embedded version...
    set "USE_SYSTEM_PYTHON=0"
)

:: DOWNLOAD & SETUP EMBEDDED PYTHON IF NECESSARY
if %USE_SYSTEM_PYTHON%==0 (
    if not exist "%PYTHON_FOLDER%" (
        echo [INFO] Downloading embedded Python...
        curl -o python.zip %PYTHON_URL%
        mkdir %PYTHON_FOLDER%
        powershell -Command "Expand-Archive -Path python.zip -DestinationPath %PYTHON_FOLDER%"
        del python.zip
    )
    set "PYTHON_CMD=%CD%\%PYTHON_FOLDER%\python.exe"
)

:: CREATE VENV IF SYSTEM PYTHON IS USED
if %USE_SYSTEM_PYTHON%==1 (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv %VENV_FOLDER%
    call %VENV_FOLDER%\Scripts\activate
)

:: INSTALL PIP (FOR EMBEDDED PYTHON)
if %USE_SYSTEM_PYTHON%==0 (
    echo [INFO] Installing PIP for Embedded Python...
    %PYTHON_CMD% -m ensurepip
    %PYTHON_CMD% -m pip install --upgrade pip
)

:: INSTALL DEPENDENCIES
echo [INFO] Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt

:: ==============================
:: USER CONFIGURATION
:: ==============================

:: ASK FOR LICENSE INFO IF NOT INSTALLED BEFORE
if %SKIP_LICENSE%==0 (
    set /p SERVER_IP="Enter server IP (e.g., 127.0.0.1): "
    set /p COMPANY_NAME="Enter company name: "

    :LICENSE_LOOP
    set /p LICENSE_KEY="Enter license key: "

    echo [INFO] Validating license...
    curl -s -X POST "%LICENSE_SERVER%?company_name=%COMPANY_NAME%&company_key=%LICENSE_KEY%&ipv4_address=%SERVER_IP%" -o license.json

    for /f "tokens=1 delims=:" %%A in ('powershell -Command "(Get-Content license.json | ConvertFrom-Json).active"') do set LICENSE_STATUS=%%A

    if "!LICENSE_STATUS!"=="True" (
        echo [INFO] License validated successfully!
    ) else (
        echo [ERROR] Invalid license key. Try again.
        goto LICENSE_LOOP
    )

    set /p APP_PORT="Enter application port (e.g., 8000): "

    :: GENERATE SECRET_KEY
    for /f %%A in ('powershell -Command "[guid]::NewGuid().ToString()"') do set SECRET_KEY=%%A

    :: CREATE .env FILE
    echo [INFO] Creating .env configuration...
    echo SERVER_IP=%SERVER_IP% > %ENV_FILE%
    echo COMPANY_NAME=%COMPANY_NAME% >> %ENV_FILE%
    echo APP_PORT=%APP_PORT% >> %ENV_FILE%
    echo LICENSE_KEY=%LICENSE_KEY% >> %ENV_FILE%
    echo SECRET_KEY=%SECRET_KEY% >> %ENV_FILE%

    del license.json
) else (
    echo [INFO] Skipping license check, using existing .env file...
)

:: ==============================
:: START THE APPLICATION
:: ==============================
echo [INFO] Starting Django application...
%PYTHON_CMD% manage.py runserver 0.0.0.0:%APP_PORT%
