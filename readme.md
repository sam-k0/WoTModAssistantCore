# ModManagerCoreGUI

The GUI application for interacting with ModManagerCore.

> [!WARNING]  
> A working (and configured) install of ModManagerCore is REQUIRED. 

### Compatibility
- Windows (10+)
- Linux (developed on Ubuntu 22 like)

MacOS/darwin support is not planned but not explicitly impossible.

### Features:
- Install, Uninstall mods
- Deactivate, Activate mods
- Import mods from previous game versions

Planned features:
- [ ] Automatic build actions for Linux
- [ ] Automatic build actions for Windows
- [ ] wgmods.net compatible mod browser integration

## Installing
Following is an unfinished guide on how to install `ModManagerCore` and `ModManagerCoreGUI`.
As for simplicity, `ModManagerCoreGUI` will just be referred to as `CoreGUI`.

### Linux

> [!TIP]
> You can also execute the `build_linux.sh` script after setting up a venv with pyside6 and pyinstaller installed.

1. Create a new directory `wotmodmanager`, and a directory called `Core` inside it.
2. Build or install the `ModManagerCore` to the newly created `wotmodmanager/Core` directory.
3. Install the CoreGUI in the parent folder, so that the `Core` directory one directory deeper as the `CoreGUI` executable.
4. Important step: Run the `ModManagerCore` executable, it will prompt you to enter your World of Tanks install directory path. This means the directory where `WorldOfTanks.exe` resides.
5. Now, run the `CoreGUI` and you should see it automatically listing mods.

### Windows
...to be done.

## Dependencies
- PySide6
- Newtonsoft.Json

Please check the project's subdirectories readme files for more information.