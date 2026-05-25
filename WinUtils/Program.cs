using WinUtils.Commands;
using WinUtils.Abstractions;

namespace WinUtils;

internal static class Program
{
    private static async Task<int> Main(string[] args)
    {
        var root = new RootCommand("WinUtils");
        var verboseOption = new Option<int?>(GlobalShared.CommandLine.VerboseGlobalOptionName, "-v", "/Verbose", "/V")
        {
            Arity     = ArgumentArity.ZeroOrMore,
            Recursive = true
        };

        root.Options.Add(verboseOption);

        var commands = new ICommandModule[]
        {
            new ClearTempCommand(),
            new SpotlightSaverCommand(),
            new DiskUsageCommand()
        };
        foreach (var command in commands)
        {
            root.Subcommands.Add(command.Build());
        }

        return await root.Parse(args).InvokeAsync();
    }
}
