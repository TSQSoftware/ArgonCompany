@echo off
setlocal EnableDelayedExpansion

:: ==============================
:: CONFIGURATION
:: ==============================
set REPO_URL=https://github.com/TSQSoftware/ArgonCompany.git
set FOLDER=ArgonCompany
set PYTHON_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip
set PYTHON_FOLDER=python_embed
set VENV_FOLDER=.venv
set ENV_FILE=.env
set LICENSE_SERVER=http://dswcsogwc84o4so88osk088c.57.129.132.234.sslip.io/api/v1/license/activate
set SKIP_LICENSE=0
set APP_PORT=8000

:: ==============================
:: CHOOSE INSTALLATION LANGUAGE
:: ==============================
echo Select installation language / Wybierz język instalacji:
echo 1. English
echo 2. Polski
set /p LANG="Enter number / Wpisz numer (1/2): "

if "%LANG%"=="1" (
    set MSG_CHECKING_PYTHON=[INFO] Checking if Python is installed...
    set MSG_USING_SYSTEM_PYTHON=[INFO] Python found! Using system Python.
    set MSG_USING_EMBEDDED_PYTHON=[INFO] Python not found. Using embedded version...
    set MSG_CREATING_VENV=[INFO] Creating virtual environment...
    set MSG_INSTALLING_DEPENDENCIES=[INFO] Installing dependencies...
    set MSG_ENTER_SERVER_IP=Enter server IP (e.g., 127.0.0.1):
    set MSG_ENTER_COMPANY_NAME=Enter company name:
    set MSG_ENTER_LICENSE_KEY=Enter license key:
    set MSG_VALIDATING_LICENSE=[INFO] Validating license...
    set MSG_INVALID_LICENSE=[ERROR] Invalid license key. Try again.
    set MSG_LICENSE_SUCCESS=[INFO] License validated successfully!
    set MSG_CREATING_ENV_FILE=[INFO] Creating .env configuration...
    set MSG_STARTING_APP=[INFO] Starting Django application...
) else (
    set MSG_CHECKING_PYTHON=[INFO] Sprawdzanie czy Python jest zainstalowany...
    set MSG_USING_SYSTEM_PYTHON=[INFO] Python znaleziony! Używam systemowego Pythona.
    set MSG_USING_EMBEDDED_PYTHON=[INFO] Python nie znaleziony. Pobieram wersję wbudowaną...
    set MSG_CREATING_VENV=[INFO] Tworzenie wirtualnego środowiska...
    set MSG_INSTALLING_DEPENDENCIES=[INFO] Instalowanie zależności...
    set MSG_ENTER_SERVER_IP=Wprowadź adres IP serwera (np. 127.0.0.1):
    set MSG_ENTER_COMPANY_NAME=Wprowadź nazwę firmy:
    set MSG_ENTER_LICENSE_KEY=Wprowadź klucz licencyjny:
    set MSG_VALIDATING_LICENSE=[INFO] Sprawdzanie licencji...
    set MSG_INVALID_LICENSE=[ERROR] Nieprawidłowy klucz licencyjny. Spróbuj ponownie.
    set MSG_LICENSE_SUCCESS=[INFO] Licencja pomyślnie zweryfikowana!
    set MSG_CREATING_ENV_FILE=[INFO] Tworzenie konfiguracji .env...
    set MSG_STARTING_APP=[INFO] Uruchamianie aplikacji Django...
)

:: ==============================
:: CHECK IF APP WAS INSTALLED BEFORE
:: ==============================
if exist "%FOLDER%\%ENV_FILE%" (
    echo [INFO] Existing installation detected, skipping license check...
    set SKIP_LICENSE=1
) else (
    set SKIP_LICENSE=0
)

:: ==============================
:: CLONE OR UPDATE REPOSITORY
:: ==============================
if exist "%FOLDER%" (
    echo [INFO] Updating existing repository...
    cd %FOLDER%
    git pull
) else (
    echo [INFO] Cloning repository...
    git clone %REPO_URL% %FOLDER%
    cd %FOLDER%
)

:: ==============================
:: CHECK IF PYTHON IS INSTALLED
:: ==============================
echo %MSG_CHECKING_PYTHON%
where python >nul 2>nul
if %errorlevel% == 0 (
    echo %MSG_USING_SYSTEM_PYTHON%
    set "USE_SYSTEM_PYTHON=1"
    set "PYTHON_CMD=python"
) else (
    echo %MSG_USING_EMBEDDED_PYTHON%
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
    echo %MSG_CREATING_VENV%
    %PYTHON_CMD% -m venv %VENV_FOLDER%
    call %VENV_FOLDER%\Scripts\activate
)

:: INSTALL PIP (FOR EMBEDDED PYTHON)
if %USE_SYSTEM_PYTHON%==0 (
    %PYTHON_CMD% -m ensurepip
    %PYTHON_CMD% -m pip install --upgrade pip
)

:: INSTALL DEPENDENCIES
echo %MSG_INSTALLING_DEPENDENCIES%
%PYTHON_CMD% -m pip install -r requirements.txt

:: ==============================
:: USER CONFIGURATION
:: ==============================
if %SKIP_LICENSE%==0 (
    set /p SERVER_IP="%MSG_ENTER_SERVER_IP% "
    set /p COMPANY_NAME="%MSG_ENTER_COMPANY_NAME% "

    :LICENSE_LOOP
    set /p LICENSE_KEY="%MSG_ENTER_LICENSE_KEY% "

    echo %MSG_VALIDATING_LICENSE%
    curl -s -X POST "%LICENSE_SERVER%?company_name=%COMPANY_NAME%&company_key=%LICENSE_KEY%&ipv4_address=%SERVER_IP%" -o license.json

    for /f "tokens=1 delims=:" %%A in ('powershell -Command "(Get-Content license.json | ConvertFrom-Json).active"') do set LICENSE_STATUS=%%A
    for /f "tokens=1 delims=:" %%A in ('powershell -Command "(Get-Content license.json | ConvertFrom-Json).uuid"') do set LICENSE_UUID=%%A

    if "!LICENSE_STATUS!"=="True" (
        echo %MSG_LICENSE_SUCCESS%
    ) else (
        echo %MSG_INVALID_LICENSE%
        goto LICENSE_LOOP
    )

    set /p APP_PORT="Enter application port (e.g., 8000): "

    :: GENERATE SECRET_KEY
    for /f %%A in ('powershell -Command "[guid]::NewGuid().ToString()"') do set SECRET_KEY=%%A

    :: CREATE .env FILE
    echo %MSG_CREATING_ENV_FILE%
    echo SERVER_IP=%SERVER_IP% > %ENV_FILE%
    echo COMPANY_NAME=%COMPANY_NAME% >> %ENV_FILE%
    echo APP_PORT=%APP_PORT% >> %ENV_FILE%
    echo LICENSE_KEY=%LICENSE_KEY% >> %ENV_FILE%
    echo UUID=%LICENSE_UUID% >> %ENV_FILE%
    echo SECRET_KEY=%SECRET_KEY% >> %ENV_FILE%

    del license.json
) else (
    echo [INFO] Skipping license check, using existing .env file...
    for /f "tokens=2 delims==" %%A in ('findstr "^APP_PORT=" %ENV_FILE%') do set APP_PORT=%%A
)

:: ==============================
:: RUN DJANGO MIGRATIONS & START APP
:: ==============================
echo [INFO] Running database migrations...
%PYTHON_CMD% manage.py migrate

echo %MSG_STARTING_APP%
%PYTHON_CMD% manage.py runserver 0.0.0.0:%APP_PORT%
