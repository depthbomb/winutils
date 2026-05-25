using WinUtils.Abstractions;
using System.Diagnostics.CodeAnalysis;

namespace WinUtils.Commands;

[SuppressMessage("Interoperability", "CA1416:Validate platform compatibility")]
public class DiskUsageCommand : ICommandModule
{
    private const string HighSpaceColor = "#26a0da";
    private const string LowSpaceColor  = "#da2626";

    #region Implementation of ICommandModule
    public Command Build()
    {
        var command = new Command("disk-usage", "Displays disk usage for all attached volumes on the system");
        command.SetAction(_ => ExecuteAsync());

        return command;
    }
    #endregion

    private async Task<int> ExecuteAsync()
    {
        var drives       = DriveInfo.GetDrives().Where(d => d.IsReady).ToList();
        var maxVolumeLen = drives.Max(d => d.VolumeLabel.Length);
        foreach (var drive in drives)
        {
            var total    = drive.TotalSize;
            var free     = drive.TotalFreeSpace;
            var used     = total - free;
            var totalStr = total.ToFileSizeString();
            var usedStr  = used.ToFileSizeString();
            var volume   = drive.VolumeLabel.PadRight(maxVolumeLen);
            var bar      = CreateProgressBar(used, total);

            Console.WriteLine($"{volume} ({drive.Name.TrimEnd('\\')}) {bar} {usedStr} used of {totalStr}");
        }

        return 0;
    }

    private string CreateProgressBar(long value, long total)
    {
        const int segments = 50;

        if (total <= 0)
            return new string('░', segments);

        var ratio      = (double)value / total;
        var filled     = (int)Math.Round(ratio * segments);
        var color      = ratio > 0.91 ? LowSpaceColor : HighSpaceColor;
        var filledPart = new string('█', filled);
        var emptyPart  = new string('█', segments - filled);

        return $"{AnsiConsole.Colorize(filledPart, color)}{AnsiConsole.Style(emptyPart, AnsiStyle.Dim)}";
    }
}
