using ModAssistant;
using Newtonsoft.Json;
using System.Diagnostics;

public class Config
{
    public string? GameInstallDir { get; set; }
}

public class ConfigIO
{
    private static string BaseConfigPath()
    {
        // If running inside Flatpak, use a writable config folder
        if (!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("FLATPAK_ID")))
        {
            string configDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), // ~/.config
                "wotmodassistant");
            Directory.CreateDirectory(configDir);
            return configDir;
        }
        else
        {
            return GetApplicationPath();
        }
    }

    private static string BaseExtractPath()
    {
        // If running inside Flatpak, use a writable folder
        if (!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("FLATPAK_ID")))
        {
            string extractDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), // ~/.local/share
                "wotmodassistant",
                "extract");
            Directory.CreateDirectory(extractDir);
            return extractDir;
        }
        else
        {
            string path = Path.Combine(GetApplicationPath(), "extract");
            if (!Directory.Exists(path))
                Directory.CreateDirectory(path);
            return path;
        }
    }

    public static string GetApplicationPath()
    {
        var process = Process.GetCurrentProcess();
        if (process.MainModule == null)
        {
            return "";
        }
        var path = process.MainModule.FileName;
        var dirname = Path.GetDirectoryName(path);
        return dirname ?? "";
    }

    public static void WriteConfig(Config config)
    {
        string json = JsonConvert.SerializeObject(config);
        string configFile = Path.Combine(BaseConfigPath(), "config.json");
        File.WriteAllText(configFile, json);
    }

    public static Config? ReadConfig()
    {
        string configFile = Path.Combine(BaseConfigPath(), "config.json");
        if (!File.Exists(configFile))
            return null;

        string json = File.ReadAllText(configFile);
        return JsonConvert.DeserializeObject<Config>(json);
    }

    public static string GetConfigPath()
    {
        return Path.Combine(BaseConfigPath(), "config.json");
    }

    public static string GetExtractFolder()
    {
        return BaseExtractPath();
    }

    public static void ClearExtractFolder()
    {
        string extractFolder = GetExtractFolder();
        if (!Directory.Exists(extractFolder))
            return;

        foreach (string dir in Directory.GetDirectories(extractFolder))
            Directory.Delete(dir, true);

        foreach (string file in Directory.GetFiles(extractFolder))
            File.Delete(file);
    }

    public static string GetModsFolderPath()
    {
        var config = ReadConfig();
        if (config == null)
            throw new Exception("Config file not found when reading mods folder path");

        return Path.Combine(config.GameInstallDir ?? throw new Exception("GameInstallDir not set"), "mods");
    }

    public static string DumpConfig()
    {
        string configFile = Path.Combine(BaseConfigPath(), "config.json");
        if (!File.Exists(configFile))
            return "Config file not found";

        return File.ReadAllText(configFile);
    }
}
