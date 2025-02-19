
[Setup]
AppName=ArgonCompany
AppVersion=1.0.0
DefaultDirName={pf}\ArgonCompany
DefaultGroupName=ArgonCompany
OutputDir=dist
OutputBaseFilename=ArgonCompany_Installer
Compression=lzma
SolidCompression=yes

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Files]
Source: "dist\ArgonCompany.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ArgonCompany"; Filename: "{app}\ArgonCompany.exe"

[Run]
Filename: "{app}\ArgonCompany.exe"; Description: "Uruchom ArgonCompany"; Flags: nowait postinstall
