using WinUtils.Abstractions;

namespace WinUtils.Commands;

public sealed class ClearTempCommand : ICommandModule
{
    private int  _totalFiles;
    private long _totalBytes;
    private int  _deletedFiles;
    private long _deletedBytes;

    #region Implementation of ICommandModule
    public Command Build()
    {
        var command   = new Command("clear-temp", "Attempts to delete all files and folders from %TEMP%.");
        var dryOption = new Option<bool?>("--dry", "-d", "/Dry", "/D");

        command.Aliases.Add("ct");
        command.Options.Add(dryOption);
        command.SetAction(r => ExecuteAsync(
            r.GetValue(dryOption),
            r.GetValue<int?>(GlobalShared.CommandLine.VerboseGlobalOptionName))
        );

        return command;
    }
    #endregion

    private async Task<int> ExecuteAsync(bool? dry, int? verbosity)
    {
        var tempDir = Environment.ExpandEnvironmentVariables("%TEMP%");
        if (!Directory.Exists(tempDir))
        {
            Console.WriteLine("Temp directory not found.");
            return 1;
        }

        try
        {
            var entries = Directory.EnumerateFileSystemEntries(tempDir, "*", SearchOption.AllDirectories);
            foreach (var entry in entries)
            {
                try
                {
                    var attr = File.GetAttributes(entry);

                    if (attr.HasFlag(FileAttributes.Directory))
                    {
                        TryToDeleteDirectory(new DirectoryInfo(entry), dry);
                    }
                    else
                    {
                        TryToDeleteFile(new FileInfo(entry), dry);
                    }
                }
                catch
                {
                    Console.WriteLine($"Unable to process: {entry}");
                }
            }

            foreach (var dir in Directory.EnumerateDirectories(tempDir, "*", SearchOption.AllDirectories).OrderByDescending(d => d.Length))
            {
                TryToDeleteDirectory(new DirectoryInfo(dir), dry);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Fatal error while clearing temp: {ex.Message}");
            return 2;
        }

        Console.WriteLine("---- Summary ----");
        Console.WriteLine($"Files scanned:\t{_totalFiles:N0}");
        Console.WriteLine($"Bytes scanned:\t{_totalBytes.ToFileSizeString()}");
        Console.WriteLine($"Files deleted:\t{_deletedFiles:N0}");
        Console.WriteLine($"Bytes deleted:\t{_deletedBytes.ToFileSizeString()}");

        return 0;
    }

    private void TryToDeleteFile(FileInfo fi, bool? dry)
    {
        try
        {
            _totalFiles++;
            _totalBytes += fi.Length;

            if (dry == true)
                return;

            var size = fi.Length;

            fi.Delete();

            _deletedFiles++;
            _deletedBytes += size;
        }
        catch
        {
            Console.WriteLine($"Unable to delete file: {fi.FullName}");
        }
    }

    private void TryToDeleteDirectory(DirectoryInfo di, bool? dry)
    {
        try
        {
            _totalFiles++;

            if (dry == true)
                return;

            di.Delete(recursive: false);

            _deletedFiles++;
        }
        catch
        {
            Console.WriteLine($"Unable to delete directory: {di.FullName}");
        }
    }
}
