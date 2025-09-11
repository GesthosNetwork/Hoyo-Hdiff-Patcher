@echo off
SetLocal EnableDelayedExpansion
chcp 65001 >nul
title GI Hdiff Patcher © 2025 GesthosNetwork

set oldVer=1.0.1
set newVer=1.1.0

set PatchFinished=False

for %%f in (Cleanup_!oldVer!-!newVer!.txt 7z.exe) do if not exist %%f (
    echo %%f is missing. & goto End
)

for /F "usebackq delims=" %%i in (Cleanup_!oldVer!-!newVer!.txt) do (
    if exist %%i (echo Deleting %%i & del %%i)
)

rd /s /q blob_storage GenshinImpact_Data\SDKCaches GenshinImpact_Data\webCaches 2>nul
del *.dmp *.bak *.log 2>nul

for %%f in (*.zip *.7z) do (
    7z.exe x %%f -o"." -y && del %%f
	set PatchFinished=True
)

:Empty
set E=0 & for /d /r GenshinImpact_Data %%i in (*) do (rd %%i 2>nul & if not exist %%i set E=1)
if !E! equ 1 goto Empty

if %PatchFinished%==True (
  (
    echo [General]
    echo channel=1
    echo cps=mihoyo
    echo game_version=!newVer!
    echo sub_channel=0
  ) > config.ini

  del *.bat *.zip *.7z hpatchz.exe 7z.exe *.txt
)

:End
pause