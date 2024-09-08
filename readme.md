# WoTModManager Core

Core functionality for WoTModManager. This tool stand-alone allows for 
- installing / uninstalling mods
- activating / deactivating mods
- searching installed mods
- moving mods to the newest game version 

Built on .NET Core, this is cross-platform, developed on Linux

### Usage: Table of Contents
1. [Help Command](#help)
2. [List Command](#list)
3. [Install Command](#install)
4. [Toggle Command](#toggle)
5. [Uninstall Command](#uninstall)
6. [Move Mods to New Version](#move-to-new)
7. [Set All Mods](#set-all)

### 1. `--help [all,keyword]`: Help Message <a name="help"></a>

**Description**: Displays help information for the mod manager.  
- Use `all` to show details of all available commands.
- Use `keyword` to get help on a specific command.

**Usage**:
```bash
mod-manager --help all # shows help for all commands
mod-manager --help install # shows help for the install command
```

### 2. `--list [all,keyword]`: List Installed Mods <a name="list"></a>

**Description**: Lists all installed mods or mods that match a keyword.

**Usage**:
```bash
mod-manager --list all # lists all installed mods
mod-manager --list xvm # lists all installed mods that contain the keyword "xvm"
```

### 3. `--install [path]`: Install a Mod <a name="install"></a>

**Description**: Installs a mod from the specified path.

**Usage**:
```bash
mod-manager --install /path/to/mod.wotmod # installs the mod from the specified path
```
### 4. `--toggle [pck_id]`: Toggle a Mod <a name="toggle"></a>

**Description**: Toggles a mod on or off.

**Usage**:
```bash
mod-manager --toggle  "example.battlehits" # toggles the mod with the pck_id "example.battlehits"
```

### 5. `--uninstall [pck_id]`: Uninstall a Mod <a name="uninstall"></a>

**Description**: Uninstalls a mod.

**Usage**:
```bash
mod-manager --uninstall "example.battlehits" # uninstalls the mod with the pck_id "example.battlehits"
```

### 6. `--move-to-new [all,keyword]`: Move Mods to New Version <a name="move-to-new"></a>

**Description**: Moves all mods from the previous to the newest game version.

**Usage**:
```bash
mod-manager --move-to-new all # move all mods
```

### 7. `--set-all [enabled, disabled]`: Set All Mods <a name="set-all"></a>

**Description**: Sets all mods to active or inactive.

**Usage**:
```bash
mod-manager --set-all enabled # enable all mods
mod-manager --set-all disabled # disable all mods
```


## Dependencies
- Newtonsoft.Json

## Building
To build the release version, run the following command:
```bash
dotnet build -c Release -r linux-x64 # for linux
dotnet build -c Release -r win-x64 # for windows
```
