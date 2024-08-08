
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
            // extract the file
            string extractFolder = ConfigIO.GetExtractFolder();
            ZipFile.ExtractToDirectory(modPath, extractFolder);
            // Check if the meta.xml file exists
            if (!File.Exists(extractFolder + "/meta.xml"))
            {
                Console.WriteLine("Error: meta.xml file not found in the .wotmod file");
                ConfigIO.ClearExtractFolder();
                return false;
            }
            // read the meta.xml file
            string xmlstr = File.ReadAllText(extractFolder + "/meta.xml");
            ModInfo mod = new ModInfo(xmlstr, true, Path.GetFileName(modPath));
            ConfigIO.ClearExtractFolder();

            // check if the mod is already installed
            List<ModInfo> installedMods = GetInstalledMods(GetNewestGameVersionFolder());

            foreach (ModInfo installedMod in installedMods)
            {
                if (installedMod.ModName == mod.ModName)
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

    }


}