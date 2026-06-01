using Caprine.FilePath;
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
        var tempDir = FilePath.TempDir();
        if (!tempDir.Exists)
        {
            Console.WriteLine("Temp directory not found.");
            return 1;
        }

        try
        {
            // Delete files first (parallel) to avoid removing directories before files are processed.
            var files = Directory.EnumerateFiles(tempDir.FullPath, "*", SearchOption.AllDirectories);
            var po    = new ParallelOptions { MaxDegreeOfParallelism = Math.Max(1, Environment.ProcessorCount) };

            Parallel.ForEach(files, po, entry =>
            {
                try
                {
                    TryToDeleteFile(new FileInfo(entry), dry);
                }
                catch
                {
                    Console.WriteLine($"Unable to process: {entry}");
                }
            });

            // Then attempt to remove empty directories from deepest to shallowest.
            var dirs = Directory.EnumerateDirectories(tempDir.FullPath, "*", SearchOption.AllDirectories).OrderByDescending(d => d.Length);
            foreach (var dir in dirs)
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
            Interlocked.Increment(ref _totalFiles);
            Interlocked.Add(ref _totalBytes, fi.Exists ? fi.Length : 0);

            if (dry == true)
                return;

            var size = fi.Exists ? fi.Length : 0;

            fi.Attributes &= ~FileAttributes.ReadOnly;
            fi.Attributes =  FileAttributes.Normal;
            fi.Delete();

            Interlocked.Increment(ref _deletedFiles);
            Interlocked.Add(ref _deletedBytes, size);
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
            Interlocked.Increment(ref _totalFiles);

            if (dry == true)
                return;

            di.Attributes &= ~FileAttributes.ReadOnly;
            di.Delete(recursive: false);

            Interlocked.Increment(ref _deletedFiles);
        }
        catch
        {
            Console.WriteLine($"Unable to delete directory: {di.FullName}");
        }
    }
}
