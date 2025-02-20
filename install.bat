@echo off
chcp 1250
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
:: CHOOSE INSTALLATION LANGUAGE (DEFAULT: ENGLISH)
:: ==============================
echo Select installation language:
echo [1] English (default)
echo [2] Polski
set /p LANG="Enter number (1/2): "

if "%LANG%"=="" set LANG=1  :: Default to English if empty
if "%LANG%"=="2" (
    set MSG_ENTER_COMPANY=Wprowadź nazwę firmy:
    set MSG_ENTER_SERVER_IP=Wprowadź adres IP serwera:
    set MSG_ENTER_LICENSE_KEY=Wprowadź klucz licencyjny:
    set MSG_VALIDATING_LICENSE=Sprawdzanie licencji...
    set MSG_INVALID_LICENSE=Nieprawidłowy klucz licencyjny. Spróbuj ponownie.
    set MSG_LICENSE_SUCCESS=Licencja zweryfikowana!
    set MSG_PYTHON_INSTALL=Instalacja Python...
    set MSG_REPO_CLONE=Pobieranie repozytorium...
    set MSG_UPDATE_REPO=Aktualizowanie repozytorium...
    set MSG_STARTING_APP=Uruchamianie aplikacji...
    set MSG_MIGRATIONS=Uruchamianie migracji Django...
) else (
    set MSG_ENTER_COMPANY=Enter company name:
    set MSG_ENTER_SERVER_IP=Enter server IP address:
    set MSG_ENTER_LICENSE_KEY=Enter license key:
    set MSG_VALIDATING_LICENSE=Validating license...
    set MSG_INVALID_LICENSE=Invalid license key. Try again.
    set MSG_LICENSE_SUCCESS=License validated successfully!
    set MSG_PYTHON_INSTALL=Installing Python...
    set MSG_REPO_CLONE=Cloning repository...
    set MSG_UPDATE_REPO=Updating repository...
    set MSG_STARTING_APP=Starting application...
    set MSG_MIGRATIONS=Running Django migrations...
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
:: CHECK & INSTALL PYTHON
:: ==============================
where python >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%A in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%A
    echo [INFO] Python detected at %PYTHON_EXE%
) else (
    echo [INFO] Python not found. Using embedded Python...
    if not exist "%PYTHON_FOLDER%" (
        mkdir "%PYTHON_FOLDER%"
        curl -o python.zip %PYTHON_URL%
        powershell -Command "Expand-Archive -Path 'python.zip' -DestinationPath '%PYTHON_FOLDER%'"
        del python.zip
    )
    set PYTHON_EXE=%CD%\%PYTHON_FOLDER%\python.exe
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
:: CREATE VIRTUAL ENVIRONMENT (IF PYTHON INSTALLED)
:: ==============================
if exist "%PYTHON_EXE%" (
    echo [INFO] Creating virtual environment...
    %PYTHON_EXE% -m venv %VENV_FOLDER%
    call %VENV_FOLDER%\Scripts\activate
) else (
    echo [ERROR] Python installation failed.
    exit /b 1
)

:: ==============================
:: INSTALL DEPENDENCIES
:: ==============================
echo [INFO] Installing dependencies...
pip install -r requirements.txt

:: ==============================
:: USER CONFIGURATION
:: ==============================
:LICENSE_LOOP
if %SKIP_LICENSE%==0 (
    :COMPANY_INPUT
    set /p COMPANY_NAME="%MSG_ENTER_COMPANY% "
    if "!COMPANY_NAME!"=="" (
        echo [ERROR] Company name cannot be empty.
        goto COMPANY_INPUT
    )

	:SERVER_IP_INPUT
	set /p SERVER_IP="%MSG_ENTER_SERVER_IP% "
	:: Remove trailing spaces
	for /f "tokens=* delims=" %%a in ("!SERVER_IP!") do set SERVER_IP=%%a
	if "!SERVER_IP!"=="" (
		echo [ERROR] Server IP cannot be empty.
		goto SERVER_IP_INPUT
	)

    :LICENSE_KEY_INPUT
    set /p LICENSE_KEY="%MSG_ENTER_LICENSE_KEY% "
    if "!LICENSE_KEY!"=="" (
        echo [ERROR] License key cannot be empty.
        goto LICENSE_KEY_INPUT
    )

    echo %MSG_VALIDATING_LICENSE%
    curl -s -X POST "%LICENSE_SERVER%?company_name="!COMPANY_NAME!"&activation_key="!LICENSE_KEY!"&ipv4_address=!SERVER_IP!" -o license.json

    if not exist license.json (
        echo [ERROR] License response is missing!
        goto LICENSE_LOOP
    )

    for /f "tokens=*" %%A in ('findstr /i "error" license.json') do (
        echo [ERROR] License error found: %%A
        echo [ERROR] License validation failed. Exiting...
        goto LICENSE_LOOP
    )

    echo %MSG_LICENSE_SUCCESS%

    echo COMPANY_NAME=!COMPANY_NAME! >> %ENV_FILE%
    echo SERVER_IP=!SERVER_IP! >> %ENV_FILE%
    echo LICENSE_KEY=!LICENSE_KEY! >> %ENV_FILE%

    set CHARS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%%^&*()_+-=[]{}|;:,.<>?/~"

    set SECRET_KEY=
    for /l %%i in (1,1,128) do (
        set /a RAND_INDEX=!random! %% 94
        for %%A in (!RAND_INDEX!) do set SECRET_KEY=!SECRET_KEY!!CHARS:~%%A,1!
    )

    echo SECRET_KEY=!SECRET_KEY! >> %ENV_FILE%
    echo [INFO] SECRET_KEY generated and saved to %ENV_FILE%

    echo DEBUG=False >> %ENV_FILE%

    :: Save server IP to address.txt in the correct folder
	> address.txt echo !SERVER_IP!
    echo [INFO] Server address !SERVER_IP! saved to address.txt

    if not "!APP_PORT!"=="" (
        echo PORT=!APP_PORT! >> %ENV_FILE%
    )
) else (
    echo [INFO] Skipping license check, using existing .env file...
)

:: ==============================
:: RUN DJANGO MIGRATIONS & START APP
:: ==============================
echo %MSG_MIGRATIONS%
python manage.py migrate

echo %MSG_STARTING_APP%
:: Read server address from file (fallback to 0.0.0.0 if missing)
if exist address.txt (
    set /p SERVER_ADDRESS=<address.txt
) else (
    set SERVER_ADDRESS=0.0.0.0
    echo [WARNING] address.txt not found. Using default address 0.0.0.0
)

if "!SERVER_ADDRESS!"=="" (
    set SERVER_ADDRESS=0.0.0.0
    echo [WARNING] address.txt is empty. Using default address 0.0.0.0
)

echo [INFO] Launching server at !SERVER_ADDRESS!:%APP_PORT%

python manage.py runserver !SERVER_ADDRESS!:%APP_PORT%