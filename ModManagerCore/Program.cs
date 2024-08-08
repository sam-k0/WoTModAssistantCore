// See https://aka.ms/new-console-template for more information
using System.Reflection;
using System.Runtime.CompilerServices;
using ModAssistant;

// Get compilation date
DateTime buildDate = new FileInfo(Assembly.GetExecutingAssembly().Location).LastWriteTime;

Console.WriteLine("Welcome to WoTModAssistant Core ver. "+buildDate.ToString("yyyy.MM.dd"));

ArgumentParser argumentParser;
try
{
    argumentParser = new ArgumentParser(args);
}
catch (ArgumentException e)
{
    Console.WriteLine("Error parsing argument: " + e.Message);
    return;
}


ModManager modManager = new ModManager();
Console.WriteLine("-> Game install directory set to "+modManager.ModManagerConfig.GameInstallDir);

foreach(ArgumentParser.Argument arg in argumentParser.ValidArguments)
{
    switch (arg.type)
    {
        case ArgumentParser.ArgumentType.Help:
            Console.WriteLine("Help message");
            break;
        case ArgumentParser.ArgumentType.Sudo:
            Console.WriteLine("Sudo command");
            break;
        case ArgumentParser.ArgumentType.Shutdown:
            Console.WriteLine("Shutdown command");
            break;
        case ArgumentParser.ArgumentType.About:
            Console.WriteLine("About command");
            break;
        case ArgumentParser.ArgumentType.List:
            Console.WriteLine("List command");
            break;
        case ArgumentParser.ArgumentType.Install:
            Console.WriteLine("Running install command");
            modManager.InstallMod(arg.value);
            break;

        default:
            Console.WriteLine("Unknown command");
            break;
    }
}


/*
List<string> strings = modManager.GetGameVersionFoldersSorted();
System.Console.WriteLine(strings.Count);
foreach (string str in strings)
{
    Console.WriteLine(str);
}

string newest = modManager.GetNewestGameVersionFolder();
Console.WriteLine(newest);

List<ModInfo> mods = modManager.GetInstalledMods(newest);
foreach (ModInfo mod in mods)
{
    System.Console.WriteLine("_--------------------------");
    Console.WriteLine(mod.ModName);
    Console.WriteLine(mod.ModID);
    Console.WriteLine(mod.Author);
    Console.WriteLine(mod.Version);
    Console.WriteLine(mod.Description);
    Console.WriteLine(mod.LocalFileName);
    Console.WriteLine(mod.IsEnabled);
}*/