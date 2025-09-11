## GI-Hdiff Patcher: a tool for manually updating Genshin Impact properly

If you update the game by simply copying all the *update files* and then replacing them in the game client directory, that's actually not the correct way. You should merge the `.pck.hdiff` update with the old `.pck` file and delete the obsolete files listed in `deletefiles.txt`.

## How to use

For example, you want to update the game from 5.4.0 to 5.5.0:

1. Place the following files in the same folder as `GenshinImpact.exe`:
   - `AudioPatch_5.4.0-5.5.0.txt`
   - `Cleanup_5.4.0-5.5.0.txt`
   - `Start.bat`
   - `hpatchz.exe`
   - `7z.exe`
   - `game_5.4.0_5.5.0_hdiff.zip`
   - `audio_xx-xx_5.4.0_5.5.0_hdiff.zip`

2. Run `Start.bat` and wait until the process finishes.
3. Now, your game is updated!

## Note

- **Update version 1.0.0 - 1.4.0**
  - From version 1.0.0 to 1.4.0, the game updates include voice audio packs for all languages.
- **Update version 1.5.0 - 2.4.0**
  - Starting from version 1.4 to 1.5, they separated game updates from voice audio pack updates.
- **Update version 2.5.0 & 2.6.0**
  - From version 2.4 to 2.5, and 2.5 to 2.6, they started using hdiff for game updates. Audio voice packs still used the old update method (non-hdiff).
- **Update version 2.7.0 - current version**
  - Starting from version 2.6 to 2.7 until the current version, they switched to using hdiff for both game updates and audio voice packs.
  
- The overview of merging process:
    ```
    Banks0.pck (59.5 MB)        // before update
    + Banks0.pck.hdiff (3.0 MB) // hdiff update
    -----------------------------
    = Banks0.pck (62.5 MB)      // new size after update
	```
