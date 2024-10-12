# ModManagerCoreGUI
[![Build for Linux](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_linux.yml/badge.svg)](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_linux.yml) [![Build for Windows](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_win.yml/badge.svg)](https://github.com/sam-k0/WoTModAssistantCore/actions/workflows/build_win.yml)

The GUI application for interacting with ModManagerCore.

> [!IMPORTANT]
> Windows is still unstable. Please report any encountered bugs.

### Compatibility
- Windows (10+)
- Linux (developed on Ubuntu 22 like)

MacOS/darwin support is not planned but not explicitly impossible.

### Features:
- Install, Uninstall mods
- Deactivate, Activate mods
- Import mods from previous game versions

Below is a screenshot of the tool running on Linux Mint 21
<br>
<div style="text-align: center;">
    <img src="https://github.com/sam-k0/WoTModAssistantCore/blob/master/res/screen1.png" alt="Description of image" width="50%"/>
</div>
<br>

Planned features:
- [x] Automatic build actions for Linux
- [x] Automatic build actions for Windows
- [ ] wgmods.net compatible mod browser integration
- [x] Easier setup of `ModManagerCore`, integrated to the GUI
- [ ] Localization / language support

## Installing
Following is an unfinished guide on how to install `ModManagerCore` and `ModManagerCoreGUI`.
> [!TIP]
> If you have trouble with automatic setup, please consult the `Manual Install`section of this readme.

### Linux

> [!TIP]
> You can also execute the `build_linux.sh` script after setting up a venv with pyside6 and pyinstaller installed.
> Also, builds can be found in the [release](https://github.com/sam-k0/WoTModAssistantCore/releases) tab.

1. Download or build the project.
2. Run `ModManagerGUI`.
3. It should prompt you to select your game directory.
4. Select the directory containing `WorldOfTanks.exe`


### Windows
> [!IMPORTANT]
> Please download the latest `Windows release` build from the [release](https://github.com/sam-k0/WoTModAssistantCore/releases) tab.

1. Download and unzip the latest release.
2. Run `ModManagerGUI.exe`.
3. On first run, it will prompt you to select the game directory, you can find it by checking the `WargamingGameCenter`->`World Of Tanks`->`Modify Installation`->`open game directory`.
4. Select the path to `WorldOfTanks.exe`.

## Manual Install & Setup

### Linux
1. Create a new directory `wotmodmanager`, and a directory called `Core` inside it.
2. Build or install the `ModManagerCore` to the newly created `wotmodmanager/Core` directory.
3. Install the CoreGUI in the parent folder, so that the `Core` directory one directory deeper as the `CoreGUI` executable.
4. Important step: Run the `ModManagerCore` executable, it will prompt you to enter your World of Tanks install directory path. This means the directory where `WorldOfTanks.exe` resides.
5. Now, run the `CoreGUI` and you should see it automatically listing mods.

### Windows
1. Download the `.zip` archive and extract.
2. Inside it, find the `_internal/Core` folder.
3. Run `ModManagerCore.exe` and set up your World Of Tanks install path (the directory where `WorldOfTanks.exe` resides.)
4. Run the `CoreGUI` from the main directory.

## Dependencies
- PySide6, PyInstaller, Python 3.11x `(ModManagerCoreGUI)`
- Newtonsoft.Json, .NET 8.0 `(ModManagerCore)`

Please check the project's subdirectories readme files for more information on how to build.

### Contributing

If you want to report bugs, request features or contribute to the project, please open an issue or a pull request.
Pull requests should be made to the `dev` branch. 
Also, please make sure your code follows `cross-platform` standards and is tested on both Windows and Linux.
Lazy or untested PRs and issues will be closed.