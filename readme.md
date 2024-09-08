# WoTModManager Core

Core functionality for WoTModManager. This tool stand-alone allows for 
- installing / uninstalling mods
- activating / deactivating mods
- searching installed mods
- moving mods to the newest game version 

Built on .NET Core, this is cross-platform, developed on Linux

## Dependencies
- Newtonsoft.Json

## Building
To build the release version, run the following command:
```bash
dotnet build -c Release -r linux-x64
```
