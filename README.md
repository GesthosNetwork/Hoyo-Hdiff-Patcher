## Hoyo-Hdiff-Patcher: a tool for manually updating Hoyo Games properly

Copying the update files directly into the game folder is not the correct update method. You must merge the `.pck.hdiff` files with the original `.pck` files and remove the outdated files listed in `deletefiles.txt`. You can perform this process using the following tool.

### Requirements
- Install [python](https://www.python.org/downloads/)

### How to use

1. Place the following files in the same folder as `exe` game:
   - `7z.exe`
   - `hpatchz.exe`
   - `patch.py`
   - `run.bat`

   for example
```
├── GenshinImpact_Data/
├── Audio_English(US)_pkg_version
├── config.ini
├── GenshinImpact.exe
├── HoYoKProtect.sys
├── mhypbase.dll
├── pkg_version
├── audio_en-us_6.3.0_6.4.0_hdiff.7z
├── game_6.3.0_6.4.0_hdiff.7z
├── 7z.exe
├── hpatchz.exe
├── patch.py
├── run.bat
```

```
├── StarRail_Data/
├── config.ini
├── GameAssembly.dll
├── HoYoKProtect.sys
├── mhypbase.dll
├── pkg_version
├── StarRail.exe
├── audio_en-us_4.0.0_4.1.0_hdiff_onQOZsbZUSMXxqsB.7z
├── game_4.0.0_4.1.0_hdiff_xvkUBFdUirbKjhAn.7z
├── 7z.exe
├── hpatchz.exe
├── patch.py
├── run.bat
```

```
├── ZenlessZoneZero_Data/
├── amd_ags_x64.dll
├── amd_fidelityfx_dx12.dll
├── Audio_English(US)_pkg_version
├── config.ini
├── file_category_launcher
├── GameAssembly.dll
├── HoYoKProtect.sys
├── ......
├── audio_en-us_2.6.0_2.7.0_hdiff_iFwzjdunKqmrHseM.zip
├── game_2.6.0_2.7.0_hdiff_xAsDGeadnSffSJTY.zip
├── UnityPlayer.dll
├── version_info
├── ZenlessZoneZero.exe
├── 7z.exe
├── hpatchz.exe
├── patch.py
├── run.bat
```

2. Click `run.bat` and wait until the process finishes.
3. Now, your game is updated!
  
- The overview of merging process:
    ```
    Banks0.pck (59.5 MB)        // before update
    + Banks0.pck.hdiff (3.0 MB) // hdiff update
    -----------------------------
    = Banks0.pck (62.5 MB)      // new size after update
	```
