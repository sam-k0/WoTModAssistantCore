// See https://aka.ms/new-console-template for more information
using System.Reflection;
using System.Runtime.CompilerServices;
using ModAssistant;
// Get compilation date
DateTime buildDate = new FileInfo(Assembly.GetExecutingAssembly().Location).LastWriteTime;

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

if (argumentParser.ValidArguments.Count == 0)
{
    Console.WriteLine("No arguments given, use --help all for help");
    return;
}


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
            modManager.ToggleMod(arg.value);
            break;
        
        case ArgumentParser.ArgumentType.List:
            var o = modManager.ListMods(arg.value);
            if(modManager.JsonOutput)
            {
                Console.WriteLine(o.GetFullJson());
            }

            break;
        case ArgumentParser.ArgumentType.Install:
            modManager.InstallMod(arg.value);
            break;

        case ArgumentParser.ArgumentType.Uninstall:
            modManager.UninstallMod(arg.value);
            break;

        case ArgumentParser.ArgumentType.MoveToNew:
            modManager.MoveToNewestGameVersion(arg.value);
            break;

        case ArgumentParser.ArgumentType.SetAll:
            if(arg.value == "enabled")
            {
                modManager.ActivateAllMods();
            
            }else if(arg.value == "disabled")
            {
                modManager.DeactivateAllMods();
            }
            break;

        case ArgumentParser.ArgumentType.Output:
            switch (arg.value)
            {
                case "json":
                    modManager.JsonOutput = true;
                    break;
                case "default":
                    modManager.JsonOutput = false;
                    break;
                default:
                    Console.WriteLine("Unknown output format");
                    break;
            }
            break;


        default:
            Console.WriteLine("Unknown command");
            break;
    }
}
