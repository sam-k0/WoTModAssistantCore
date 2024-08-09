using System.ComponentModel;
using System.Runtime.CompilerServices;
using Regex = System.Text.RegularExpressions.Regex;

public class ArgumentParser
{

    // argument list with get method
    public List<Argument> ValidArguments {  get; private set;} = new List<Argument>();

    /**
    Arguments:
    -c, --color: Set the color of the LED: Allowed values: [0-255, 0-255, 0-255], whitespaces optional between values
    -h, --help: Show help message: allowed values(one of): all, color, help, about
    **/

    public enum ArgumentType
    {
        [Description("Help message.")]
        Help,

        [Description("Sudo command.")]
        Sudo,

        [Description("Exits and clears cache.")]
        Shutdown,

        [Description("About message.")]
        About,

        [Description("List mods: (all) shows all mods, or enter search term.")]
        List,

        [Description("Install mod. needs the path to the mod package file.")]
        Install,

        [Description("Toggle mod active / inactive, needs the package ID.")]
        Toggle,

        [Description("Uninstall mod, needs the package ID.")]
        Uninstall,

        [Description("Move mods from previous version to the newest game version, needs: package ID, or: all to move all")]
        MoveToNew,

        [Description("Set all mods to active / inactive, allowed values: enabled, disabled")]
        SetAll,
    }

    public struct Argument{
        public string option; // ex. --help , -h
        public ArgumentType type; // the discrete type of the argument
        public string value; // the value of the argument

        public Argument(string option, ArgumentType type, string value)
        {
            this.option = option;
            this.type = type;
            this.value = value;
        }
    }

    Dictionary<string, string> argumentFormat = new Dictionary<string, string>
    {
        {"-h", ".*"},
        {"--help", ".*"},
        {"--sudo", "true|false"},
        // shutdown can be any string
        {"--shutdown", ".*"},
        {"--exit", ".*"},
        {"--info", ".*"},
        {"-l", ".*|all"}, // list mods
        {"--list", ".*|all"},
        {"--install", ".*"}, // install mod
        {"-i", ".*"},
        {"--toggle", ".*"}, // toggle mod active / inactive
        {"--uninstall", ".*"}, // uninstall mod
        {"--move-to-new", ".*"}, // move mod to new location
        {"--set-all", "enabled|disabled"}, // set all mods to active / inactive
    };


    

    public ArgumentParser(string[] args)
    {
        if (args.Length % 2 != 0)
        {
            throw new ArgumentException("Invalid argument list");
        }

        // Check if the arguments are in the Dictionary of options
        for (int i = 0; i < args.Length; i += 2)
        {
            if (!argumentFormat.ContainsKey(args[i]))
            {
                throw new ArgumentException($"Invalid argument (err1): {args[i]}");
            }

            // Check if the value of the argument is valid
            if (!Regex.IsMatch(args[i + 1], argumentFormat[args[i]]))
            {
                throw new ArgumentException($"Invalid value for argument: {args[i]}");
            }
        }

        // add them to the validPairs list
        for (int i = 0; i < args.Length; i += 2)
        {
            //parse option to ArgumentType
            ArgumentType type = args[i] switch
            {
                "-h" => ArgumentType.Help,
                "--help" => ArgumentType.Help,
                "--sudo" => ArgumentType.Sudo,
                "--shutdown" => ArgumentType.Shutdown, // both lead to the same action
                "--exit" => ArgumentType.Shutdown,
                "--about" => ArgumentType.About,
                "-l" => ArgumentType.List,
                "--list" => ArgumentType.List,
                "-i" => ArgumentType.Install,
                "--install" => ArgumentType.Install,
                "--toggle" => ArgumentType.Toggle,
                "--uninstall" => ArgumentType.Uninstall,
                "--move-to-new" => ArgumentType.MoveToNew,
                "--set-all" => ArgumentType.SetAll,
                
                _ => throw new ArgumentException($"Invalid argument (err2): {args[i]}")
            };

            ValidArguments.Add(new Argument(args[i], type, args[i + 1]));
        }
    }

    public string CallHelp(string value)
    {
        string help = "Showing help for "+value+" command:\n";
        switch (value)
        {
            case "all": 
                help = "Showing help page for "+value;
                break;
            
            case "list":
                help += EnumHelper.GetEnumDescription(ArgumentType.List);
                break;

            case "help":
                help += EnumHelper.GetEnumDescription(ArgumentType.Help);
                break;

            case "install":
                help += EnumHelper.GetEnumDescription(ArgumentType.Install);
                break;

            case "toggle":
                help += EnumHelper.GetEnumDescription(ArgumentType.Toggle);
                break;

            case "uninstall":
                help += EnumHelper.GetEnumDescription(ArgumentType.Uninstall);
                break;
            
            case "move-to-new":
                help += EnumHelper.GetEnumDescription(ArgumentType.MoveToNew);
                break;
            
            case "set-all":
                help += EnumHelper.GetEnumDescription(ArgumentType.SetAll);
                break;


            default:
                return("Invalid value for help argument");
        }
        return help;
    }
}