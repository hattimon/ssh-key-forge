!define PRODUCT_NAME "SSH Key Forge"
!define PRODUCT_EXE "SSHKeyForge.exe"
!define PRODUCT_PUBLISHER "Kosmo"
!define PRODUCT_VERSION "1.0.1"
!define INSTALL_DIR "$PROGRAMFILES\\SSH Key Forge"

Name "${PRODUCT_NAME}"
OutFile "..\\dist\\SSHKeyForge-Setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKCU "Software\\${PRODUCT_NAME}" "InstallDir"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!include "MUI2.nsh"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File "..\\dist\\SSHKeyForge.exe"
  File "..\\icon.ico"
  WriteRegStr HKCU "Software\\${PRODUCT_NAME}" "InstallDir" "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\\${PRODUCT_NAME}"
  CreateShortcut "$SMPROGRAMS\\${PRODUCT_NAME}\\${PRODUCT_NAME}.lnk" "$INSTDIR\\${PRODUCT_EXE}" "" "$INSTDIR\\icon.ico"
  CreateShortcut "$DESKTOP\\${PRODUCT_NAME}.lnk" "$INSTDIR\\${PRODUCT_EXE}" "" "$INSTDIR\\icon.ico"
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\${PRODUCT_EXE}"
  Delete "$INSTDIR\\icon.ico"
  Delete "$INSTDIR\\Uninstall.exe"
  Delete "$SMPROGRAMS\\${PRODUCT_NAME}\\${PRODUCT_NAME}.lnk"
  Delete "$DESKTOP\\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\\${PRODUCT_NAME}"
  RMDir "$INSTDIR"
  DeleteRegKey HKCU "Software\\${PRODUCT_NAME}"
SectionEnd



