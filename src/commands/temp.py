from typing import cast
from src.app import app
from pathlib import Path
from tempfile import gettempdir
from foxcli.command import Command
from src.lib.utils import human_size

@app.register()
class ClearTemp(Command):
    name = 'clear-temp'
    description = 'Clears all files and directories in %TEMP%'
    def __init__(self):
        super().__init__()

        self.deleted_items = cast(list[Path], [])
        self.errored_items = cast(list[Path], [])
        self.deleted_bytes = 0

    def _delete_item(self, path: Path):
        try:
            if path.is_dir():
                path.rmdir()
            elif path.is_file():
                self.deleted_bytes += path.stat().st_size
                path.unlink(missing_ok=True)

            self.deleted_items.append(path)
        except OSError as e:
            self.errored_items.append(path)
            if e.winerror == 5:
                self.ctx.stdout.write('\nCannot delete file %s because it is in use' % path.name)
            elif e.winerror == 145:
                self.ctx.stdout.write('\nCannot delete non-empty directory %s likely because it contains in-use files' % path.name)
        except Exception as e:
            self.errored_items.append(path)
            self.ctx.stdout.write('\nFailed to delete %s: %s' % (path.name, e))

    def run(self, args):
        temp_dir = Path(gettempdir())
        all_paths = list(temp_dir.glob('**/*'))

        temp_files = [p for p in all_paths if p.is_file()]
        temp_dirs = sorted([p for p in all_paths if p.is_dir()], reverse=True)

        for path in temp_files + temp_dirs:
            self._delete_item(path)

        if self.deleted_items:
            self.ctx.stdout.write('\nSuccessfully deleted %s item(s) totalling %s' % (format(len(self.deleted_items)), human_size(self.deleted_bytes)))

        if self.errored_items:
            self.ctx.stdout.write('\nCould not delete %s item(s)' % format(len(self.errored_items)))

        return 0
