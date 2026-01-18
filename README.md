## Hoyo-Hdiff-Patcher: a tool for manually updating Hoyo Games properly

Copying the update files directly into the game folder is not the correct update method. You must merge the `.pck.hdiff` files with the original `.pck` files and remove the outdated files listed in `deletefiles.txt`. You can perform this process using the following tool.

## How to use

1. Place the following files in the same folder as `GenshinImpact.exe`:
   - `7z.exe`
   - `hpatchz.exe`
   - `patch.py`
   - `run.bat`

2. Click `run.bat` and wait until the process finishes.
3. Now, your game is updated!
  
- The overview of merging process:
    ```
    Banks0.pck (59.5 MB)        // before update
    + Banks0.pck.hdiff (3.0 MB) // hdiff update
    -----------------------------
    = Banks0.pck (62.5 MB)      // new size after update
	```
