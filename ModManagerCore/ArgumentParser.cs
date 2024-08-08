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
        Help,
        Sudo,
        Shutdown,
        About,
        List,
        Install,
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
        {"-h", "all|list|help|about"},
        {"--help", "all|list|help|about"},
        {"--sudo", "true|false"},
        // shutdown can be any string
        {"--shutdown", ".*"},
        {"--exit", ".*"},
        {"--info", ".*"},
        {"-l", ".*|all"},
        {"--list", ".*|all"},
        {"--install", ".*"},
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
                "--info" => ArgumentType.About,
                "-l" => ArgumentType.List,
                "--list" => ArgumentType.List,
                "-i" => ArgumentType.Install,
                "--install" => ArgumentType.Install,


                _ => throw new ArgumentException($"Invalid argument (err2): {args[i]}")
            };

            ValidArguments.Add(new Argument(args[i], type, args[i + 1]));
        }
    }
}