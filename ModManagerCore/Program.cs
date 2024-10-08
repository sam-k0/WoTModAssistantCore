﻿// See https://aka.ms/new-console-template for more information
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


Output output;
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
            output= modManager.ToggleMod(arg.value);
            if(modManager.JsonOutput)
            {
                Console.WriteLine(output.GetFullJson());
            }
            break;
        
        case ArgumentParser.ArgumentType.List:
            output= modManager.ListMods(arg.value);
            if(modManager.JsonOutput)
            {
                Console.WriteLine(output.GetFullJson());
            }

            break;
        case ArgumentParser.ArgumentType.Install:
            output=modManager.InstallMod(arg.value);
            if(modManager.JsonOutput)
            {
                Console.WriteLine(output.GetFullJson());
            }
            break;

        case ArgumentParser.ArgumentType.Uninstall:
            output = modManager.UninstallMod(arg.value);
            if (modManager.JsonOutput)
            {
                Console.WriteLine(output.GetFullJson());
            }
            break;

        case ArgumentParser.ArgumentType.MoveToNew:
            output = modManager.MoveToNewestGameVersion(arg.value);
            if (modManager.JsonOutput)
            {
                Console.WriteLine(output.GetFullJson());
            }
            break;

        case ArgumentParser.ArgumentType.SetAll:
            if(arg.value == "enabled")
            {
                output = modManager.ActivateAllMods();
                if (modManager.JsonOutput)
                {
                    Console.WriteLine(output.GetFullJson());
                }
            
            }else if(arg.value == "disabled")
            {
                output = modManager.DeactivateAllMods();
                if (modManager.JsonOutput)
                {
                    Console.WriteLine(output.GetFullJson());
                }
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
        
        case ArgumentParser.ArgumentType.ModFolders:
            output= modManager.GetModFolders(arg.value);
            if(modManager.JsonOutput)
            {
                Console.WriteLine(output.GetFullJson());
            }
            break;


        default:
            Console.WriteLine("Unknown command");
            break;
    }
}
