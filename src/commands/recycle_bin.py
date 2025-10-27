from typing import cast
from src.app import app
from foxcli.option import Opt
from ctypes import byref, sizeof
from foxcli.command import Command
from src.lib.utils import human_size
from src.commands.formattable import FormattableCommand
from src.lib.native import (
    SHQUERYRBINFO,
    SHERB_NOSOUND,
    SHERB_NOPROGRESSUI,
    SHQueryRecycleBinW,
    SHEmptyRecycleBinW,
    SHERB_NOCONFIRMATION
)

@app.register()
class RecycleBin(Command):
    name = 'recycle-bin'

@app.register(parent='recycle-bin')
class RecycleBinQuery(FormattableCommand):
    name = 'query'
    description = 'Returns info about items in the Recycle Bin'

    def run(self, args):
        info = SHQUERYRBINFO()
        info.cbSize = sizeof(info)

        hr = SHQueryRecycleBinW(None, byref(info))

        items_count = cast(int, info.i64NumItems)
        items_bytes = cast(int, info.i64Size)
        items_size = human_size(items_bytes)

        if args.get('format', str) == 'json':
            self.writeln({
                'totalSizeBytes': items_bytes,
                'totalSize': items_size,
                'numItems': items_count,
            })
        else:
            if items_count:
                self.writeln('There are %d items totaling %s in the Recycle Bin' % (items_count, items_size))
            else:
                self.writeln('The Recycle Bin is empty')

        return 0

@app.register(parent='recycle-bin')
class RecycleBinEmpty(FormattableCommand):
    name = 'empty'
    description = 'Empties the Recycle Bin'
    options = [
        Opt('show-confirmation', default=False, help='Shows the confirmation message box before items are emptied'),
        Opt('show-progress-ui', default=False, help='Shows the progress dialog box as the Recycle Bin is being emptied'),
        Opt('play-sound', default=False, help='Plays the emptying sound on supported systems'),
    ]

    def _empty(self, flags: int):
        # TODO handle errors better
        try:
            SHEmptyRecycleBinW(None, None, flags)
            return True
        except OSError:
            return False

    def run(self, args):
        flags = 0

        if not args.get('show-confirmation', bool):
            flags |= SHERB_NOCONFIRMATION

        if not args.get('show-progress-ui', bool):
            flags |= SHERB_NOPROGRESSUI

        if not args.get('play-sound', bool):
            flags |= SHERB_NOSOUND

        has_emptied = self._empty(flags)

        if args.get('format', str) == 'plain':
            if has_emptied:
                self.writeln('Emptied the Recycle Bin')
            else:
                self.writeln('No items to empty out')
        else:
            self.writeln({
                'emptied': has_emptied,
            })

        return 0
