
using System.Diagnostics.CodeAnalysis;
using Newtonsoft.Json;
using System.Diagnostics;
using System.IO.Compression;
using System.Reflection.Metadata.Ecma335;

namespace ModAssistant
{
    public enum ErrorCode {
        Success = 0,
        FilesystemFailed = 1,
        ModNotFound = 2,
    }
    public enum ActionCode
    {
        Install = 0,
        Uninstall = 1,
        Toggle = 2,
        MoveToNew = 3,
        SetAll = 4,
        List = 5,
        GetFolders = 6,
    }
    public struct Output {
        public string message;
        public ErrorCode errorCode;
        public ActionCode actionCode;

        public Output(string message, ErrorCode code, ActionCode actionCode)
        {
            this.message = message;
            this.errorCode = code;
            this.actionCode = actionCode;
        }

        public string GetFullJson()
        {
            return JsonConvert.SerializeObject(this);
        }
    }
    public class ModManager
    {
        public Config? ModManagerConfig { get; private set; }
        public bool JsonOutput { get; set; } = false;

        private Output LogOutput(string message, ErrorCode code, ActionCode actionCode )
        {
            Output output = new Output(message, code, actionCode);
            if(!JsonOutput)
            {
                Console.WriteLine(output.message);
            }
            return output;
        }

        // Get current app path, used for storing configs
        private Config? LoadConfig()
        {
            ConfigIO configIO = new ConfigIO();
            // check if config exists
            if (ConfigIO.ReadConfig() == null)
            {
                // ask user for game install dir
                Console.WriteLine("Please enter the path to your World of Tanks installation directory (Contains WorldOfTanks.exe):");
                var installdir = Console.ReadLine();
                // check if path is valid
                while (!Directory.Exists(installdir) || !File.Exists(installdir + "/WorldOfTanks.exe"))
                {
                    Console.WriteLine("Invalid path, please enter a valid path:");
                    installdir = Console.ReadLine();
                }

                // create config
                Config config = new Config();
                config.GameInstallDir = installdir;
                ConfigIO.WriteConfig(config);

                Console.WriteLine("Successfully found game install directory: " + installdir);
            }   
            // Now, we can safely assume that the config exists and read it
            if (ConfigIO.ReadConfig() == null)
            {
                throw new Exception("Config file not found after safely creating it");
            }
            return ConfigIO.ReadConfig();
        }

        public string GetNewestGameVersionFolder()
        {
            List<string> items = GetGameVersionFoldersSorted();
            return items[items.Count - 1];
        }

        public List<string> GetGameVersionFoldersSorted()
        {
            List<string> items = new List<string>();

            foreach (string subdirectory in Directory.EnumerateDirectories(ConfigIO.GetModsFolderPath()))
            {
                // check if the subdirectory is a valid game version folder or the config or temp folder, we only want to get the game version folders
                if (subdirectory.Contains("config") || subdirectory.Contains("temp"))
                {
                    continue;
                }
                items.Add(subdirectory);
            }
            items.Sort();
            return items;
        }

        // Will always be json output
        public Output GetModFolders(string keyword)
        {
            if(keyword == "newest")
            {
                return new Output(JsonConvert.SerializeObject(GetNewestGameVersionFolder()), ErrorCode.Success, ActionCode.GetFolders);
            }
            else if(keyword == "all")
            {
                return new Output(JsonConvert.SerializeObject(GetGameVersionFoldersSorted()), ErrorCode.Success, ActionCode.GetFolders);
            }
            else
            {
                return new Output("Invalid keyword", ErrorCode.FilesystemFailed, ActionCode.GetFolders);
            }  
        }

        public List<ModInfo> GetInstalledMods(string gameVersionFolder)
        {
            List<ModInfo> mods = new List<ModInfo>();
            // We are in the game version folder, so we can iterate over the .wotmod files
            // but in order to read the metadata, we need to extract the files to the extract folder
            // and read the metadata from the xml file
            foreach (string file in Directory.EnumerateFiles(gameVersionFolder, "*.wotmod"))
            {
                // extract the file
                string extractFolder = ConfigIO.GetExtractFolder();
                ZipFile.ExtractToDirectory(file, extractFolder);
                ModInfo mod;
                // Check if the meta.xml file exists
                if (!File.Exists(extractFolder + "/meta.xml"))
                {
                    mod = new ModInfo(Path.GetFileName(file), "unknown", Path.GetFileName(file),
                                    "0.0.0", "No description available", Path.GetFileName(file));
                    mods.Add(mod);
                    // Clean up
                    ConfigIO.ClearExtractFolder();
                    continue;
                }
                string xmlstr = File.ReadAllText(extractFolder + "/meta.xml");
                mod = new ModInfo(xmlstr, true, Path.GetFileName(file));
                mods.Add(mod);
                // Clean up
                ConfigIO.ClearExtractFolder();
            }
            // Disabled mods end with .wotmod.disabled
            foreach (string file in Directory.EnumerateFiles(gameVersionFolder, "*.wotmod.disabled"))
            {
                // extract the file
                string extractFolder = ConfigIO.GetExtractFolder();
                ZipFile.ExtractToDirectory(file, extractFolder);
                ModInfo mod;
                // Check if the meta.xml file exists
                if (!File.Exists(extractFolder + "/meta.xml"))
                {
                    mod = new ModInfo(Path.GetFileName(file), "unknown", Path.GetFileName(file),
                                    "0.0.0", "No description available", Path.GetFileName(file), false);
                    mods.Add(mod);
                    // Clean up
                    ConfigIO.ClearExtractFolder();
                    continue;
                }
                string xmlstr = File.ReadAllText(extractFolder + "/meta.xml");
                mod = new ModInfo(xmlstr, false, Path.GetFileName(file));
                mod.IsEnabled = false;
                mods.Add(mod);
                // Clean up
                ConfigIO.ClearExtractFolder();
            }
            return mods;

        }

        public ModManager()
        {
            ConfigIO.ClearExtractFolder(); // Clean up, maybe the user closed the app while extracting
            ModManagerConfig = LoadConfig();
            if (ModManagerConfig == null)
            {
                throw new Exception("Config file not found after loading it");
            }
            
        }

        // Expects the whole path to the .wotmod file
        public ModInfo GetModInfo(string modPath)
        {
            // extract the file
            string extractFolder = ConfigIO.GetExtractFolder();
            ZipFile.ExtractToDirectory(modPath, extractFolder);
            // Check if the meta.xml file exists
            if (!File.Exists(extractFolder + "/meta.xml"))
            {
                Console.WriteLine("Error: meta.xml file not found in the .wotmod file");
                ConfigIO.ClearExtractFolder();
                ModInfo modInfo = new ModInfo(Path.GetFileName(modPath), "unknown", Path.GetFileName(modPath),
                                    "0.0.0", "No description available", Path.GetFileName(modPath));
                return modInfo;
            }
            // read the meta.xml file
            string xmlstr = File.ReadAllText(extractFolder + "/meta.xml");
            ModInfo mod = new ModInfo(xmlstr, false, Path.GetFileName(modPath));
            ConfigIO.ClearExtractFolder();
            return mod;
        }

        // Expects the whole path to the .wotmod file
        public Output InstallMod(string modPath)
        {

            ConfigIO.ClearExtractFolder();
            // check if the file exists
            if (!File.Exists(modPath))
            {
                return LogOutput("Referenced file does not exist", ErrorCode.FilesystemFailed, ActionCode.Install);
            }
            // check if the file is a .wotmod file
            if (!modPath.EndsWith(".wotmod"))
            {
                return LogOutput("Referenced file is not a .wotmod file", ErrorCode.FilesystemFailed, ActionCode.Install);
            }
            
            ModInfo mod = GetModInfo(modPath);

            // check if the mod is already installed
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());

            foreach (ModInfo installedMod in installedMods)
            {
                if (installedMod.PackageID == mod.PackageID)
                {
                    // check if the current version is newer by comparing the version numbers as integers
                    try
                    {
                        if (int.Parse(installedMod.Version.Replace(".", "")) < int.Parse(mod.Version.Replace(".", "")))
                        {
                            // move the file to the mods folder
                            File.Move(modPath, GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath));
                            // Clean up
                            ConfigIO.ClearExtractFolder();

                            return LogOutput(
                                "Installed mod to " + GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath),
                                ErrorCode.Success,
                                ActionCode.Install);
                        }
                        else
                        {
                            ConfigIO.ClearExtractFolder();
                            return LogOutput(
                                "A mod with the same name is already installed, and the version is the same or older",
                                ErrorCode.Success, ActionCode.Install);
                        }
                    }
                    catch (Exception e)
                    {
                        ConfigIO.ClearExtractFolder();
                        return LogOutput("Error comparing version numbers between mods: " + e.Message, ErrorCode.FilesystemFailed, ActionCode.Install);
                    }
                }
            }
            // move the file to the mods folder
            File.Move(modPath, GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath));
            // Clean up
            ConfigIO.ClearExtractFolder();
            return LogOutput("Installed mod to " + GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath),
                             ErrorCode.Success,
                             ActionCode.Install);
        }

        public Output UninstallMod(string pkID)
        {
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (mod.PackageID == pkID)
                {
                    // Delete the file
                    File.Delete(GetNewestGameVersionFolder() + "/" + mod.LocalFileName);
                    
                    return LogOutput("Uninstalled mod " + mod.ModName+ $" ({mod.PackageID})", ErrorCode.Success, ActionCode.Uninstall);
                }
            }
            return LogOutput("Mod not found", ErrorCode.ModNotFound, ActionCode.Uninstall);
        }

        public Output ToggleMod(string pkID){
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (mod.PackageID == pkID)
                {
                    // Check if the mod is enabled
                    if (mod.IsEnabled)
                    {
                        // Disable the mod
                        File.Move(GetNewestGameVersionFolder() + "/" + mod.LocalFileName, GetNewestGameVersionFolder() + "/" + mod.LocalFileName + ".disabled");                        
                        return LogOutput("Disabled mod " + mod.ModName+ $" ({mod.PackageID})", ErrorCode.Success, ActionCode.Toggle);
                    }
                    else
                    {
                        // Enable the mod
                        // Remove the .disabled extension
                        string nameWithoutDisabled = mod.LocalFileName.Substring(0, mod.LocalFileName.Length - ".disabled".Length);
                        File.Move(GetNewestGameVersionFolder() + "/" + mod.LocalFileName, GetNewestGameVersionFolder() + "/" + nameWithoutDisabled);
                        return LogOutput("Enabled mod " + mod.ModName+ $" ({mod.PackageID})", ErrorCode.Success, ActionCode.Toggle);
                    }
                }
            }
            Console.WriteLine("Mod not found");
            return LogOutput("Mod not found", ErrorCode.ModNotFound, ActionCode.Toggle);
        }

        public Output ActivateAllMods()
        {
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (!mod.IsEnabled)
                {
                    // Remove the .disabled extension
                    string nameWithoutDisabled = mod.LocalFileName.Substring(0, mod.LocalFileName.Length - ".disabled".Length);
                    File.Move(GetNewestGameVersionFolder() + "/" + mod.LocalFileName, GetNewestGameVersionFolder() + "/" + nameWithoutDisabled);
                }
            }
            return LogOutput("Activated all mods", ErrorCode.Success, ActionCode.SetAll);
        }

        public Output DeactivateAllMods()
        {
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (mod.IsEnabled)
                {
                    // Disable the mod
                    File.Move(GetNewestGameVersionFolder() + "/" + mod.LocalFileName, GetNewestGameVersionFolder() + "/" + mod.LocalFileName + ".disabled");
                }
            }
            return LogOutput("Deactivated all mods", ErrorCode.Success, ActionCode.SetAll);
        }

        public Output ListMods(string keyword)
        {
            List<string> outputs = new List<string>();
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (mod.ModName.Contains(keyword) ||(keyword == "all"))
                {
                    switch (JsonOutput)
                    {
                        case true:
                            string json = JsonConvert.SerializeObject(mod);
                            //System.Console.WriteLine(json);
                            outputs.Add(json); // Add the json string to the list
                            break;
                        case false:
                            Console.WriteLine("-----------------------");
                            Console.WriteLine(mod.ToString());
                            break;
                    }
                }
            }
            return new Output(JsonConvert.SerializeObject(outputs), ErrorCode.Success, ActionCode.List);
        }

        public Output MoveToNewestGameVersion(string pkID)
        {
            List<string> items = GetGameVersionFoldersSorted();
            if (items.Count < 2)
            {
                return LogOutput("Not enough game version folders to move mods", ErrorCode.FilesystemFailed, ActionCode.MoveToNew);
            }
            string newest = items[items.Count - 1];
            string secondNewest = items[items.Count - 2];
            // If move all or a specific mod
            if (pkID == "all")
            {
                // Move all mods from the second newest game version folder to the newest game version folder
                
                foreach (string file in Directory.EnumerateFiles(secondNewest, "*.wotmod"))
                {
                    try
                    {
                        File.Move(file, newest + "/" + Path.GetFileName(file));
                    }
                    catch (Exception e)
                    {
                        System.Console.WriteLine("Error moving file: " + e.Message);
                    }
                }
                var num = Directory.EnumerateFiles(secondNewest, "*.wotmod").ToList().Count();
                return LogOutput("Moved " + num + " mods from " + secondNewest + " to " + newest, ErrorCode.Success, ActionCode.MoveToNew);
            }
            List<ModInfo> installedMods = GetInstalledMods(secondNewest);
            foreach (ModInfo mod in installedMods)
            {
                if (mod.PackageID == pkID)
                {
                    File.Move(secondNewest + "/" + mod.LocalFileName, newest + "/" + mod.LocalFileName);
                    return LogOutput("Moved mod " + mod.ModName + $" ({mod.PackageID}) from " + secondNewest + " to " + newest, ErrorCode.Success, ActionCode.MoveToNew);
                }
            }
           return LogOutput("Mod not found", ErrorCode.ModNotFound, ActionCode.MoveToNew);
        }

    }


}