using Microsoft.Win32;
using Caprine.FilePath;
using WinUtils.Abstractions;
using System.Diagnostics.CodeAnalysis;

namespace WinUtils.Commands;

[SuppressMessage("Interoperability", "CA1416:Validate platform compatibility")]
public class SpotlightSaverCommand : ICommandModule
{
    private int _savedFiles;

    #region Implementation of ICommandModule
    public Command Build()
    {
        var command       = new Command("spotlight-saver", "Saves the Windows Spotlight lockscreen images to\"Pictures\\Windows Spotlight\"");
        var startupOption = new Option<bool?>("--startup");

        command.Aliases.Add("ss");
        command.Options.Add(startupOption);
        command.SetAction(r => ExecuteAsync(r.GetValue(startupOption)));

        return command;
    }
    #endregion

    private async Task<int> ExecuteAsync(bool? startup)
    {
        if (startup == true)
        {
            if (TryToggleStartup(out var enabled))
            {
                Console.WriteLine(enabled ? "Command will now be ran on startup." : "Command will no longer be ran on startup.");
                return 0;
            }

            Console.WriteLine("Unable to toggle startup.");
            return 1;
        }

        var assetsDir = FilePath.From(Environment.ExpandEnvironmentVariables("%LOCALAPPDATA%"))        / "Packages" / "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy" / "LocalState" / "Assets";
        var saveDir   = FilePath.From(Environment.GetFolderPath(Environment.SpecialFolder.MyPictures)) / "Windows Spotlight";
        saveDir.Mkdir(existOk: true);
        var files = Directory.EnumerateFiles(assetsDir.FullPath, "*", SearchOption.TopDirectoryOnly);
        foreach (var file in files)
        {
            var imageName = Path.GetFileNameWithoutExtension(file);

            if (!TryGetImageDimensions(file, out var dimensions))
            {
                Console.WriteLine($"{imageName} is not a valid JPEG, skipping.");
                continue;
            }

            var width  = dimensions.Item1;
            var height = dimensions.Item2;
            if (width != 1920 && height != 1080)
            {
                Console.WriteLine($"{imageName} is not a proper desktop wallpaper resolution, skipping.");
                continue;
            }

            var imagePath = saveDir / $"{imageName}.jpg";
            if (imagePath.Exists)
            {
                Console.WriteLine($"{imageName} has already been saved, skipping.");
                continue;
            }

            var originalBytes = await File.ReadAllBytesAsync(file);

            await imagePath.WriteBytesAsync(originalBytes);

            Console.WriteLine($"Saved {imageName}.");

            _savedFiles++;
        }

        if (_savedFiles > 0)
        {
            Console.WriteLine($"Saved {_savedFiles} new Windows Spotlight image(s).");
        }

        return 0;
    }

    private bool TryToggleStartup(out bool enabled)
    {
        enabled = false;

        try
        {
            const string path      = @"Software\Microsoft\Windows\CurrentVersion\Run";
            const string valueName = "WinUtils";

            var exePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "winutils.exe");
            var command = $"\"{exePath}\" ss";

            using var key = Registry.CurrentUser.OpenSubKey(path, true)
                            ?? throw new InvalidOperationException("Unable to open registry Run key");

            var existing = key.GetValue(valueName) as string;
            if (!string.IsNullOrWhiteSpace(existing))
            {
                key.DeleteValue(valueName, throwOnMissingValue: false);
            }
            else
            {
                key.SetValue(valueName, command, RegistryValueKind.String);

                enabled = true;
            }

            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private bool TryGetImageDimensions(string path, out Tuple<int, int> dimensions)
    {
        dimensions = new Tuple<int, int>(0, 0);

        using var stream = File.OpenRead(path);
        using var reader = new BinaryReader(stream);

        if (reader.ReadByte() != 0xFF || reader.ReadByte() != 0xD8)
        {
            return false;
        }

        while (stream.Position < stream.Length)
        {
            var prefix = reader.ReadByte();
            if (prefix != 0xFF)
            {
                return false;
            }

            var marker = reader.ReadByte();
            while (marker == 0xFF)
            {
                marker = reader.ReadByte();
            }

            if (marker is 0xD8 or 0xD9)
            {
                continue;
            }

            var length = ReadUInt16BE(reader);
            var isSof = marker is 0xC0 or 0xC1 or 0xC2 or 0xC3 or
                                  0xC5 or 0xC6 or 0xC7 or
                                  0xC9 or 0xCA or 0xCB or
                                  0xCD or 0xCE or 0xCF;
            if (isSof)
            {
                reader.ReadByte();

                var height = ReadUInt16BE(reader);
                var width  = ReadUInt16BE(reader);

                dimensions = new Tuple<int, int>(width, height);

                return true;
            }

            stream.Seek(length - 2, SeekOrigin.Current);
        }

        return false;
    }

    private ushort ReadUInt16BE(BinaryReader reader)
    {
        int hi = reader.ReadByte();
        int lo = reader.ReadByte();

        return (ushort)(hi << 8 | lo);
    }
}
