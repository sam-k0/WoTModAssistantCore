
using System.Diagnostics.CodeAnalysis;
using Newtonsoft.Json;
using System.Diagnostics;
using System.IO.Compression;

namespace ModAssistant
{
    public class ModManager
    {
        public Config ModManagerConfig { get; private set; }
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
        public bool InstallMod(string modPath)
        {
            ConfigIO.ClearExtractFolder();
            // check if the file exists
            if (!File.Exists(modPath))
            {
                Console.WriteLine("File does not exist");
                return false;
            }
            // check if the file is a .wotmod file
            if (!modPath.EndsWith(".wotmod"))
            {
                Console.WriteLine("File is not a .wotmod file");
                return false;
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
                            Console.WriteLine("Mod is already installed, but this version is newer");
                            // move the file to the mods folder
                            File.Move(modPath, GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath));
                            System.Console.WriteLine("Installed mod to " + GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath));
                            // Clean up
                            ConfigIO.ClearExtractFolder();
                            return true;
                        }
                        else
                        {
                            Console.WriteLine("A mod with the same name is already installed, and the version is the same or older");
                            ConfigIO.ClearExtractFolder();
                            return false;
                        }
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine("Error comparing version numbers: " + e.Message);
                        ConfigIO.ClearExtractFolder();
                        return false;
                    }
                }
            }
            // move the file to the mods folder
            File.Move(modPath, GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath));
            System.Console.WriteLine("Installed mod to " + GetNewestGameVersionFolder() + "/" + Path.GetFileName(modPath));
            // Clean up
            ConfigIO.ClearExtractFolder();
            return true;
        }

        public bool UninstallMod(string pkID)
        {
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (mod.PackageID == pkID)
                {
                    // Delete the file
                    File.Delete(GetNewestGameVersionFolder() + "/" + mod.LocalFileName);
                    System.Console.WriteLine("Uninstalled mod " + mod.ModName + $" ({mod.PackageID})");
                    return true;
                }
            }
            Console.WriteLine("Mod not found");
            return false;
        }

        public bool ToggleMod(string pkID){
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
                        System.Console.WriteLine("Disabled mod " + mod.ModName+ $" ({mod.PackageID})");
                        return true;
                    }
                    else
                    {
                        // Enable the mod
                        // Remove the .disabled extension
                        string nameWithoutDisabled = mod.LocalFileName.Substring(0, mod.LocalFileName.Length - ".disabled".Length);

                        File.Move(GetNewestGameVersionFolder() + "/" + mod.LocalFileName, GetNewestGameVersionFolder() + "/" + nameWithoutDisabled);
                        System.Console.WriteLine("Enabled mod " + mod.ModName+ $" ({mod.PackageID})");
                        return true;
                    }
                }
            }
            Console.WriteLine("Mod not found");
            return false;
        }

        public bool ActivateAllMods()
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
            System.Console.WriteLine("Activated all mods");
            return true;
        }

        public bool DeactivateAllMods()
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
            System.Console.WriteLine("Deactivated all mods");
            return true;
        }

        public void ListMods(string keyword)
        {
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());
            foreach (ModInfo mod in installedMods)
            {
                if (mod.ModName.Contains(keyword) ||(keyword == "all"))
                {
                    System.Console.WriteLine("-----------------------");
                    System.Console.WriteLine(mod.ToString());
                }
            }
        }

        public void MoveToNewestGameVersion(string pkID)
        {
            List<string> items = GetGameVersionFoldersSorted();
            if (items.Count < 2)
            {
                System.Console.WriteLine("Not enough game version folders to move mods");
                return;
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
                System.Console.WriteLine("Moved "+num+" mods from " + secondNewest + " to " + newest);
                return;
            }
            List<ModInfo> installedMods = GetInstalledMods(secondNewest);
            foreach (ModInfo mod in installedMods)
            {
                if (mod.PackageID == pkID)
                {
                    File.Move(secondNewest + "/" + mod.LocalFileName, newest + "/" + mod.LocalFileName);
                    System.Console.WriteLine("Moved mod " + mod.ModName + $" ({mod.PackageID}) from " + secondNewest + " to " + newest);
                    return;
                }
            }
            System.Console.WriteLine("Mod ${pkID} not found in " + secondNewest);
        }

    }


}