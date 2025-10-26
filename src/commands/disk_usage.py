from src.app import App
from subprocess import run
from typing import TypedDict
from src.lib.ansi import style, colorize
from src.lib.utils import human_size, parse_csv_str
from src.commands.formattable import FormattableCommand

class HotFixRecord(TypedDict):
    Caption: str
    FreeSpace: int
    Size: int
    VolumeName: str

class DiskUsageCommand(FormattableCommand):
    """
    Displays disk usage for all attached volumes on the system
    """
    def __init__(self):
        super().__init__()

        self.high_space_color = '#26a0da'
        self.low_space_color = '#da2626'

    def _create_progress_bar(self, value: int, total: int):
        segments = 50
        ratio = value / total
        filled = round(ratio * segments)
        color = self.low_space_color if ratio > 0.91 else self.high_space_color

        return '%s%s' % (colorize('█' * filled, fg_color=color), style('█' * (segments - filled), 'dim'))

    def run(self, app: App):
        res = run(['wmic', 'logicaldisk', 'get', 'size,freespace,caption,volumename', '/format:csv'], text=True, capture_output=True, check=True)
        records = parse_csv_str(res.stdout)

        if self.format == 'plain':
            volume_name_max_len = max((len(r['VolumeName']) for r in records), default=0)
            for record in records:
                total_size_bytes = int(record['Size'])
                free_space_bytes = int(record['FreeSpace'])
                used_space_bytes = total_size_bytes - free_space_bytes

                total_size = human_size(total_size_bytes)
                used_space = human_size(used_space_bytes)
                volume_name = record['VolumeName'].ljust(volume_name_max_len)

                self.writeln('%s (%s) %s %s used of %s' % (volume_name, record['Caption'], self._create_progress_bar(used_space_bytes, total_size_bytes), used_space, total_size))
        else:
            data = []
            for record in records:
                total_size_bytes = int(record['Size'])
                free_space_bytes = int(record['FreeSpace'])
                used_space_bytes = total_size_bytes - free_space_bytes

                total_size = human_size(total_size_bytes)
                free_space = human_size(free_space_bytes)
                used_space = human_size(used_space_bytes)

                data.append({
                    'driveLetter': record['Caption'].replace(':', ''),
                    'volumeName': record['VolumeName'],
                    'totalSizeBytes': total_size_bytes,
                    'freeSpaceBytes': free_space_bytes,
                    'usedSpaceBytes': used_space_bytes,
                    'totalSize': total_size,
                    'freeSpace': free_space,
                    'usedSpace': used_space,
                })

            self.writeln(data)

        return 0
