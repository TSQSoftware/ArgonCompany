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
set "LOG_FILE=argon_install.log"

:: ==============================
:: LOGGING SETUP
:: ==============================
echo [INFO] Script started at %DATE% %TIME% > "%LOG_FILE%"
echo Logging to %LOG_FILE%...

:: ==============================
:: NETWORK CONNECTIVITY CHECK
:: ==============================
echo [INFO] Checking network connectivity...
ping -n 1 github.com >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No internet connection. Ensure network access before running the script. >> "%LOG_FILE%"
    echo [ERROR] No internet connection. Ensure network access before running the script.
    exit /b 1
)

:: ==============================
:: INSTALLATION OF GIT
:: ==============================
where git >nul 2>nul || (
    echo [INFO] Git not found. Installing Git... >> "%LOG_FILE%"
    curl -o git_installer.exe %GIT_INSTALLER_URL%
    if exist git_installer.exe (
        start /wait "" git_installer.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to install Git. >> "%LOG_FILE%"
            echo [ERROR] Failed to install Git.
            exit /b 1
        )
        del git_installer.exe
    ) else (
        echo [ERROR] Failed to download Git installer. >> "%LOG_FILE%"
        echo [ERROR] Failed to download Git installer.
        exit /b 1
    )
)

:: ==============================
:: PYTHON INSTALLATION
:: ==============================
if not exist "%PYTHON_FOLDER%" (
    echo [INFO] Downloading embedded Python... >> "%LOG_FILE%"
    curl -o python.zip %PYTHON_URL%
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download Python. >> "%LOG_FILE%"
        echo [ERROR] Failed to download Python.
        exit /b 1
    )

    echo [INFO] Extracting Python... >> "%LOG_FILE%"
    tar -xf python.zip -C "%CD%" >nul 2>nul || (
        echo [ERROR] Failed to extract Python. >> "%LOG_FILE%"
        echo [ERROR] Failed to extract Python.
        exit /b 1
    )
    del python.zip
)

set "PYTHON_EXE=%CD%\%PYTHON_FOLDER%\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python installation failed. >> "%LOG_FILE%"
    echo [ERROR] Python installation failed.
    exit /b 1
)

:: ==============================
:: INSTALLING PIP (IF NEEDED)
:: ==============================
if not exist "%PYTHON_FOLDER%\Scripts\pip.exe" (
    echo [INFO] Installing pip... >> "%LOG_FILE%"
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    "%PYTHON_EXE%" get-pip.py
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install pip. >> "%LOG_FILE%"
        echo [ERROR] Failed to install pip.
        exit /b 1
    )
    del get-pip.py
)

:: ==============================
:: CLONE OR UPDATE REPOSITORY
:: ==============================
if exist "%FOLDER%" (
    echo [INFO] Updating existing repository... >> "%LOG_FILE%"
    cd "%FOLDER%"
    git pull
) else (
    echo [INFO] Cloning repository... >> "%LOG_FILE%"
    git clone "%REPO_URL%" "%FOLDER%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to clone repository. >> "%LOG_FILE%"
        echo [ERROR] Failed to clone repository.
        exit /b 1
    )
    cd "%FOLDER%"
)

:: ==============================
:: VIRTUAL ENVIRONMENT SETUP
:: ==============================
if exist "%VENV_FOLDER%" (
    echo [INFO] Removing old virtual environment... >> "%LOG_FILE%"
    rmdir /s /q "%VENV_FOLDER%"
)

echo [INFO] Creating virtual environment... >> "%LOG_FILE%"
"%PYTHON_EXE%" -m venv "%VENV_FOLDER%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment. >> "%LOG_FILE%"
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
)

call "%VENV_FOLDER%\Scripts\activate.bat"

echo [INFO] Installing dependencies... >> "%LOG_FILE%"
pip install -r requirements.txt || (
    echo [ERROR] Dependency installation failed. >> "%LOG_FILE%"
    echo [ERROR] Dependency installation failed.
    exit /b 1
)

:: ==============================
:: LICENSE HANDLING
:: ==============================
if not exist "%ENV_FILE%" (
    set SKIP_LICENSE=0
) else (
    echo [INFO] Existing installation detected, skipping license activation... >> "%LOG_FILE%"
    set SKIP_LICENSE=1
)

if %SKIP_LICENSE%==0 (
    :LICENSE_LOOP
    set /p "COMPANY_NAME=Enter company name: "
    if "!COMPANY_NAME!"=="" (
        echo [ERROR] Company name cannot be empty.
        goto LICENSE_LOOP
    )

    set /p "SERVER_IP=Enter server IP address: "
    if "!SERVER_IP!"=="" (
        echo [ERROR] Server IP address cannot be empty.
        goto LICENSE_LOOP
    )

    set /p "LICENSE_KEY=Enter license key: "
    if "!LICENSE_KEY!"=="" (
        echo [ERROR] License key cannot be empty.
        goto LICENSE_LOOP
    )

    echo [INFO] Validating license... >> "%LOG_FILE%"
    curl -s -X POST "%LICENSE_SERVER%?company_name=!COMPANY_NAME!&activation_key=!LICENSE_KEY!&ipv4_address=!SERVER_IP!" -o license.json
    if not exist license.json (
        echo [ERROR] License validation failed. Retry... >> "%LOG_FILE%"
        echo [ERROR] License validation failed. Retry...
        goto LICENSE_LOOP
    )

    echo [INFO] License validated successfully! >> "%LOG_FILE%"
)

echo [INFO] Script completed successfully. >> "%LOG_FILE%"
echo [INFO] Script completed successfully.
exit /b 0
