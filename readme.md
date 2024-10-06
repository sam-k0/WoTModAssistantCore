# ModManagerCoreGUI
[![Build for Linux](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_linux.yml/badge.svg)](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_linux.yml) [![Build for Windows](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_win.yml/badge.svg)](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_win.yml)

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
- [x] Automatic build actions for Linux
- [x] Automatic build actions for Windows
- [ ] wgmods.net compatible mod browser integration
- [ ] Easier setup of `ModManagerCore`, integrated to the GUI

## Installing
Following is an unfinished guide on how to install `ModManagerCore` and `ModManagerCoreGUI`.
As for simplicity, `ModManagerCoreGUI` will just be referred to as `CoreGUI`.

### Linux

> [!TIP]
> You can also execute the `build_linux.sh` script after setting up a venv with pyside6 and pyinstaller installed.
> Also, builds can be found as `artifacts` in the `Actions` tab.

1. Create a new directory `wotmodmanager`, and a directory called `Core` inside it.
2. Build or install the `ModManagerCore` to the newly created `wotmodmanager/Core` directory.
3. Install the CoreGUI in the parent folder, so that the `Core` directory one directory deeper as the `CoreGUI` executable.
4. Important step: Run the `ModManagerCore` executable, it will prompt you to enter your World of Tanks install directory path. This means the directory where `WorldOfTanks.exe` resides.
5. Now, run the `CoreGUI` and you should see it automatically listing mods.

### Windows
> [!IMPORTANT]
> Please download the latest `artifacts` build from the `actions->Build Windows` workflow run.

1. Download the `.zip` archive and extract.
2. Inside it, find the `_internal/Core` folder.
3. Run `ModManagerCore.exe` and set up your World Of Tanks install path (the directory where `WorldOfTanks.exe` resides.)
4. Run the `CoreGUI` from the main directory.

## Dependencies
- PySide6
- Newtonsoft.Json

Please check the project's subdirectories readme files for more information.
