@echo off
SetLocal EnableDelayedExpansion
chcp 65001 >nul
Title GI Hdiff Patcher © 2025 GesthosNetwork

set oldVer=5.5.0
set newVer=5.6.0

set PatchFinished=False

set audio=GenshinImpact_Data\StreamingAssets\AudioAssets
set path1=%audio%\English(US)
set path2=%audio%\Japanese
set path3=%audio%\Korean
set path4=%audio%\Chinese

for %%f in (AudioPatch_!oldVer!-!newVer!.txt Cleanup_!oldVer!-!newVer!.txt 7z.exe hpatchz.exe) do if not exist %%f (
    echo %%f is missing. & goto End
)

for /F "usebackq delims=" %%i in (Cleanup_!oldVer!-!newVer!.txt) do (
    if exist %%i (echo Deleting %%i & del %%i)
)

rd /s /q blob_storage ldiff GenshinImpact_Data\StreamingAssets\Audio GenshinImpact_Data\SDKCaches GenshinImpact_Data\webCaches 2>nul
del *.dmp *.bak *.log 2>nul

for %%f in (*.zip *.7z) do (
    7z.exe x %%f -o"." -y && del %%f
)

for %%i in (!path1!, !path2!, !path3!, !path4!) do if not exist "%%i\*.hdiff" rd /s /q %%i 2>nul

if not exist %path1% del /f /q Audio_English(US)_pkg_version 2>nul
if not exist %path2% del /f /q Audio_Japanese_pkg_version 2>nul
if not exist %path3% del /f /q Audio_Chinese_pkg_version 2>nul
if not exist %path4% del /f /q Audio_Korean_pkg_version 2>nul

set audio_lang_14=GenshinImpact_Data\Persistent\audio_lang_14
set "used_language="
md GenshinImpact_Data\Persistent > nul 2>&1 & type nul > !audio_lang_14!

if exist !path1! (
    set /p="English(US)" <nul >> !audio_lang_14!
    set "used_language=English(US)"
)
if exist !path2! (
    if defined used_language echo. >> !audio_lang_14!
    set /p=Japanese <nul >> !audio_lang_14!
    set used_language=Japanese
)
if exist !path3! (
    if defined used_language echo. >> !audio_lang_14!
    set /p=Korean <nul >> !audio_lang_14!
    set "used_language=Korean"
)
if exist !path4! (
    if defined used_language echo. >> !audio_lang_14!
    set /p=Chinese <nul >> !audio_lang_14!
    set used_language=Chinese
)

for /F "usebackq delims=" %%i in (AudioPatch_!oldVer!-!newVer!.txt) do (
    hpatchz.exe -f %%i %%i.hdiff %%i && del %%i.hdiff 2>nul
    set PatchFinished=True
)

:Empty
set E=0 & for /d /r GenshinImpact_Data %%i in (*) do (rd %%i 2>nul & if not exist %%i set E=1)
if !E! equ 1 goto Empty

if %PatchFinished%==True (
  (
    echo [General]
    echo channel=1
    echo cps=hoyoverse
    echo game_version=!newVer!
    echo sub_channel=0
  ) > config.ini

  del *.bat *.zip *.7z hpatchz.exe 7z.exe *.txt *.bak
)

:End
pause