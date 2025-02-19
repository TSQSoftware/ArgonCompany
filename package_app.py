import os
import subprocess
import sys

MAIN_SCRIPT = "manage.py"
PROJECT_NAME = "ArgonCompany"

def get_version():
    return "1.0.0"

VERSION = get_version()

def create_spec():
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(['{MAIN_SCRIPT}'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['django', 'ninja'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)
pkg = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(pkg, a.scripts, [],
          exclude_binaries=True,
          name='{PROJECT_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
    """
    with open("app.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

def build_exe():
    if os.path.exists("app.spec"):
        os.remove("app.spec")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "manage.py"])

def create_inno_script():
    inno_script = f"""
[Setup]
AppName={PROJECT_NAME}
AppVersion={VERSION}
DefaultDirName={{pf}}\{PROJECT_NAME}
DefaultGroupName={PROJECT_NAME}
OutputDir=dist
OutputBaseFilename={PROJECT_NAME}_Installer
Compression=lzma
SolidCompression=yes

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Files]
Source: "dist\{PROJECT_NAME}.exe"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\{PROJECT_NAME}"; Filename: "{{app}}\{PROJECT_NAME}.exe"

[Run]
Filename: "{{app}}\{PROJECT_NAME}.exe"; Description: "Uruchom {PROJECT_NAME}"; Flags: nowait postinstall
"""
    with open("installer.iss", "w", encoding="utf-8") as f:
        f.write(inno_script)

def build_installer():
    subprocess.run(["ISCC", "installer.iss"])

if __name__ == "__main__":
    create_spec()
    build_exe()
    create_inno_script()
    build_installer()
    print("Instalator gotowy!")
