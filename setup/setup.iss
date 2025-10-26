[Setup]
AppId={{C63A0864-4DC8-43AB-886C-2919BC51702C}
AppName={#NameLong}
AppVersion={#Version}
AppVerName={#NameLong} {#Version}
AppPublisher={#Company}
AppPublisherURL={#RepoUrl}
AppSupportURL={#IssuesUrl}
AppUpdatesURL={#ReleasesUrl}
AppCopyright={#Copyright}
VersionInfoVersion={#Version}
DefaultDirName={autopf}\{#Company}\{#NameLong}
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=admin
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\build
OutputBaseFilename=winutils-setup
SetupIconFile=..\resources\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
MinVersion=10.0
WizardStyle=modern
WizardResizable=no
ShowTasksTreeLines=yes
UninstallDisplayIcon={app}\{#ExeName}
UninstallDisplayName={#NameLong} - {#Description}
VersionInfoCompany={#Company}
VersionInfoCopyright={#Copyright}
VersionInfoProductName={#NameLong}
VersionInfoProductVersion={#Version}
VersionInfoProductTextVersion={#Version}
VersionInfoDescription={#Description}

[Code]
const EnvironmentKey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';

procedure EnvAddPath(Path: string);
var
  Paths: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Paths) then
    Paths := '';

  if Pos(';' + Uppercase(Path) + ';', ';' + Uppercase(Paths) + ';') > 0 then exit;

  Paths := Paths + ';' + Path;

  if RegWriteStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Paths) then
    Log(Format('The [%s] added to PATH: [%s]', [Path, Paths]))
  else
    Log(Format('Error while adding the [%s] to PATH: [%s]', [Path, Paths]));
end;

procedure EnvRemovePath(Path: string);
var
  Paths: string;
  P: Integer;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Paths) then
    exit;

  P := Pos(';' + Uppercase(Path) + ';', ';' + Uppercase(Paths) + ';');
  if P = 0 then exit;

  Delete(Paths, P - 1, Length(Path) + 1);

  if RegWriteStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Paths) then
    Log(Format('The [%s] removed from PATH: [%s]', [Path, Paths]))
  else
    Log(Format('Error while removing the [%s] from PATH: [%s]', [Path, Paths]));
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    EnvAddPath(ExpandConstant('{app}'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    EnvRemovePath(ExpandConstant('{app}'));
end;

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\build\src.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion

[UninstallDelete]
Type: dirifempty; Name: "{app}"
