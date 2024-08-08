using ModAssistant;
using Newtonsoft.Json;
using System.Diagnostics;

public class Config
{// config properties
    public string ?GameInstallDir { get; set; }

}

public class ConfigIO
{
    public static string GetApplicationPath()
    {
        var process = Process.GetCurrentProcess();
        if (process.MainModule == null)
        {
            return "";
        }
        var path = process.MainModule.FileName;
        var dirname = Path.GetDirectoryName(path);
        if (dirname == null)
        {
            return "";
        }
        return dirname;
    }

    public static void WriteConfig(Config config)
    {
        string json = JsonConvert.SerializeObject(config);
        File.WriteAllText(GetApplicationPath() +"/config.json", json);
    }

    public static Config? ReadConfig()
    {
        if (!File.Exists(GetApplicationPath()+"/config.json"))
        {
            return null;
        }
        string json = File.ReadAllText(GetApplicationPath()+"/config.json");
        return JsonConvert.DeserializeObject<Config>(json);
    }

    public static string GetConfigPath()
    {
        return GetApplicationPath()+"/config.json";
    }  

    public static string GetExtractFolder()
    {
        // make sure the folder exists
        if (!Directory.Exists(GetApplicationPath()+"/extract"))
        {
            Directory.CreateDirectory(GetApplicationPath()+"/extract");
        }

        return GetApplicationPath()+"/extract";
    }

    public static void ClearExtractFolder()
    {
        //System.Console.WriteLine("Clearing extract folder at " + GetExtractFolder());
        string[] subDirectories = Directory.GetDirectories(GetExtractFolder());

        // Delete each subdirectory
        foreach (string subDirectory in subDirectories)
        {
            //System.Console.WriteLine("Deleting: " + subDirectory);
            Directory.Delete(subDirectory, true);
        }
        // Delete all files
        string[] files = Directory.GetFiles(GetExtractFolder());
        foreach (string file in files)
        {
            //System.Console.WriteLine("Deleting: " + file);
            File.Delete(file);
        }

    }

    public static string GetModsFolderPath()
    {
        if(ReadConfig() == null)
        {
            throw new Exception("Config file not found when reading mods folder path");
        }
        return Path.Combine(ReadConfig().GameInstallDir, "mods");
    }

    public static string DumpConfig()
    {
        if (!File.Exists(GetApplicationPath()+"/config.json"))
        {
            return "Config file not found";
        }
        return File.ReadAllText(GetApplicationPath()+"/config.json");
    }
}