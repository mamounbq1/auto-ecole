; Script Inno Setup pour Auto-École Manager
; Créé par: e.belqasim@gmail.com
; Version: 1.0.0

#define MyAppName "Auto-École Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Auto-École Manager"
#define MyAppURL "https://autoecole-manager.ma"
#define MyAppExeName "AutoEcoleManager.exe"
#define MyAppContact "e.belqasim@gmail.com"
#define MyAppPhone "+212 637-636146"

[Setup]
; Informations de l'application
AppId={{8F9A2B3C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppContact={#MyAppContact}

; Répertoire d'installation par défaut
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Licence et informations
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALL_INFO.txt
InfoAfterFile=AFTER_INSTALL.txt

; Sortie de l'installeur
OutputDir=installer
OutputBaseFilename=AutoEcoleManager_Setup_v{#MyAppVersion}
SetupIconFile=assets\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/max
SolidCompression=yes

; Privilèges
PrivilegesRequired=admin

; Style visuel
WizardStyle=modern
WizardImageFile=assets\installer_banner.bmp
WizardSmallImageFile=assets\installer_icon.bmp

; Langues
ShowLanguageDialog=no

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Raccourcis:"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "Créer un raccourci dans la barre de lancement rapide"; GroupDescription: "Raccourcis:"; Flags: unchecked
Name: "startupicon"; Description: "Lancer au démarrage de Windows"; GroupDescription: "Options supplémentaires:"; Flags: unchecked

[Files]
; Exécutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Icônes et images
Source: "assets\app_icon.png"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\app_icon_new.png"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\app_icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\installer_banner.png"; DestDir: "{app}\assets"; Flags: ignoreversion

; Scripts utilitaires
Source: "generate_license.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "scripts\setup_database.py"; DestDir: "{app}\scripts"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "installer\README.txt"; DestDir: "{app}"; Flags: ignoreversion

; Créer les répertoires nécessaires
[Dirs]
Name: "{app}\data"; Permissions: users-full
Name: "{app}\config"; Permissions: users-full
Name: "{app}\backups"; Permissions: users-full
Name: "{app}\exports"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Icons]
; Menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Comment: "Lancer {#MyAppName}"
Name: "{group}\Générateur de Licence"; Filename: "python"; Parameters: """{app}\generate_license.py"""; IconFilename: "{app}\assets\app_icon.ico"; Comment: "Générer une licence"
Name: "{group}\Aide et Support"; Filename: "{app}\README.txt"; Comment: "Documentation et support"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"; Comment: "Désinstaller l'application"

; Bureau
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: desktopicon; Comment: "{#MyAppName} - Gestion d'Auto-École"

; Barre de lancement rapide
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: quicklaunchicon

; Démarrage automatique (optionnel)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: startupicon

[Run]
; Initialiser la base de données au premier lancement
Filename: "python"; Parameters: """{app}\scripts\setup_database.py"""; StatusMsg: "Initialisation de la base de données..."; Flags: runhidden waituntilterminated; Check: IsPythonInstalled

; Proposer de lancer l'application
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName} maintenant"; Flags: nowait postinstall skipifsilent

; Ouvrir le dossier d'installation
Filename: "{win}\explorer.exe"; Parameters: """{app}"""; Description: "Ouvrir le dossier d'installation"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
; Supprimer les fichiers de logs lors de la désinstallation
Type: filesandordirs; Name: "{app}\logs"

[Code]
// Vérifier si Python est installé (pour les scripts utilitaires)
function IsPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// Message de bienvenue personnalisé
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Bienvenue dans l''installation de ' + '{#MyAppName}' + #13#10#13#10 +
         'Cet assistant va installer l''application sur votre ordinateur.' + #13#10#13#10 +
         'Version: {#MyAppVersion}' + #13#10 +
         'Support: {#MyAppContact}' + #13#10 +
         'Téléphone: {#MyAppPhone}', 
         mbInformation, MB_OK);
end;

// Vérifier l'espace disque requis
function NextButtonClick(CurPageID: Integer): Boolean;
var
  DiskSpace: Integer;
begin
  Result := True;
  
  if CurPageID = wpSelectDir then
  begin
    DiskSpace := GetSpaceOnDisk(ExtractFileDrive(WizardDirValue), True);
    if DiskSpace < 500 * 1024 * 1024 then // 500 MB requis
    begin
      MsgBox('Espace disque insuffisant!' + #13#10 +
             'L''installation nécessite au moins 500 MB d''espace libre.' + #13#10 +
             'Espace disponible: ' + IntToStr(DiskSpace div (1024*1024)) + ' MB',
             mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// Message après installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Créer un fichier de première installation
    SaveStringToFile(ExpandConstant('{app}\FIRST_RUN.txt'), 
                     'Première installation: ' + GetDateTimeString('dd/mm/yyyy hh:nn', #0, #0), 
                     False);
  end;
end;

// Message de fin d'installation
procedure DeinitializeSetup();
begin
  if WizardIsTaskSelected('desktopicon') then
    MsgBox('Un raccourci a été créé sur votre bureau.' + #13#10#13#10 +
           'Pour commencer:' + #13#10 +
           '1. Double-cliquez sur l''icône' + #13#10 +
           '2. Utilisez admin / Admin123! pour vous connecter' + #13#10 +
           '3. Générez une licence si nécessaire' + #13#10#13#10 +
           'Support: {#MyAppContact}',
           mbInformation, MB_OK);
end;
