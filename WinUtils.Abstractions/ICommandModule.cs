using System.CommandLine;

namespace WinUtils.Abstractions;

public interface ICommandModule
{
    Command Build();
}
