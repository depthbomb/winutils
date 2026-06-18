using Windows.Win32;
using Windows.Win32.System.Console;

namespace WinUtils;

public enum AnsiStyle
{
    Dim,
    Bold,
}

public static class AnsiConsole
{
    private const string Reset = "\e[0m";

    private static readonly bool Enabled;

    static AnsiConsole()
    {
        Enabled = EnableAnsiIfPossible();
    }

    public static string Colorize(string text, string hexColor)
    {
        if (!Enabled)
            return text;

        var (r, g, b) = HexToRgb(hexColor);
        var start = $"\e[38;2;{r};{g};{b}m";

        return $"{start}{text}{Reset}";
    }

    public static string Style(string text, AnsiStyle style)
    {
        if (!Enabled)
            return text;

        return style switch
        {
            AnsiStyle.Dim  => $"\e[2m{text}\e[0m",
            AnsiStyle.Bold => $"\e[1m{text}\e[0m",
            _              => text
        };
    }

    public static void StartTabSpinner()
    {
        Console.Write("\e]9;4;3;0\a");
    }

    public static void StopTabSpinner()
    {
        Console.Write("\e]9;4;0;0\a");
    }

    private static (int r, int g, int b) HexToRgb(string hex)
    {
        hex = hex.TrimStart('#');

        var r = Convert.ToInt32(hex.Substring(0, 2), 16);
        var g = Convert.ToInt32(hex.Substring(2, 2), 16);
        var b = Convert.ToInt32(hex.Substring(4, 2), 16);

        return (r, g, b);
    }

    private static bool EnableAnsiIfPossible()
    {
        if (!OperatingSystem.IsWindows())
            return true;

        var handle = PInvoke.GetStdHandle_SafeHandle(STD_HANDLE.STD_OUTPUT_HANDLE);
        if (handle is null)
            return false;

        if (!PInvoke.GetConsoleMode(handle, out var mode))
            return false;

        mode |= CONSOLE_MODE.ENABLE_VIRTUAL_TERMINAL_PROCESSING;

        return PInvoke.SetConsoleMode(handle, mode);
    }
}
