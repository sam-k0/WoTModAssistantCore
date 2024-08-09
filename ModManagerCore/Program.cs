// See https://aka.ms/new-console-template for more information
using System.Reflection;
using System.Runtime.CompilerServices;
using ModAssistant;

// Get compilation date
DateTime buildDate = new FileInfo(Assembly.GetExecutingAssembly().Location).LastWriteTime;

Console.WriteLine("WoTModAssistant Core ver. "+buildDate.ToString("yyyy.MM.dd"));

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


foreach(ArgumentParser.Argument arg in argumentParser.ValidArguments)
{
    switch (arg.type)
    {
        case ArgumentParser.ArgumentType.Help:
            Console.WriteLine(argumentParser.CallHelp(arg.value));
            break;
        case ArgumentParser.ArgumentType.Sudo:
            Console.WriteLine("Sudo command");
            break;
        case ArgumentParser.ArgumentType.Shutdown:
            Console.WriteLine("Clearing cache before shutdown");

            break;
        case ArgumentParser.ArgumentType.About:
            Console.WriteLine("------ About ------");
            Console.WriteLine("WoTModAssistant Core ver. "+buildDate.ToString("yyyy.MM.dd"));
            Console.WriteLine("This tool is used to manage mods for World of Tanks\nThe tool is used to install, uninstall, enable, disable and move mods to the newest game version");
            Console.WriteLine("-> Game install directory set to "+modManager.ModManagerConfig.GameInstallDir);

            break;

        case ArgumentParser.ArgumentType.Toggle:
            Console.WriteLine("Toggling mod: "+ arg.value);
            modManager.ToggleMod(arg.value);
            break;
        
        case ArgumentParser.ArgumentType.List:
            Console.WriteLine("Listing mods: "+ arg.value);
            modManager.ListMods(arg.value);

            break;
        case ArgumentParser.ArgumentType.Install:
            Console.WriteLine("Running install command");
            modManager.InstallMod(arg.value);
            break;

        case ArgumentParser.ArgumentType.Uninstall:
            Console.WriteLine("Running uninstall command");
            modManager.UninstallMod(arg.value);
            break;

        case ArgumentParser.ArgumentType.MoveToNew:
            Console.WriteLine("Running move-to-new command");
            modManager.MoveToNewestGameVersion(arg.value);
            break;

        case ArgumentParser.ArgumentType.SetAll:
            Console.WriteLine("Running set-all command");
            if(arg.value == "enabled")
            {
                modManager.ActivateAllMods();
            
            }else if(arg.value == "disabled")
            {
                modManager.DeactivateAllMods();
            }
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