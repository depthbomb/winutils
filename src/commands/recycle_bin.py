from src.app import App
from foxcli.option import Opt
from ctypes import byref, sizeof
from typing import cast, Annotated
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

class RecycleBinQueryCommand(FormattableCommand):
    """
    Returns info about items in the Recycle Bin
    """
    def run(self, app: App):
        info = SHQUERYRBINFO()
        info.cbSize = sizeof(info)

        hr = SHQueryRecycleBinW(None, byref(info))

        items_count = cast(int, info.i64NumItems)
        items_bytes = cast(int, info.i64Size)
        items_size = human_size(items_bytes)

        if self.format == 'json':
            self.writeln({
                'totalSizeBytes': items_bytes,
                'totalSize': items_size,
                'numItems': items_count,
            })
        else:
            if items_count:
                self.writeln('There are %d items totally %s in the Recycle Bin' % (items_count, items_size))
            else:
                self.writeln('The Recycle Bin is empty')

        return 0

class RecycleBinEmptyCommand(FormattableCommand):
    """
    Empties the Recycle Bin
    """
    show_confirmation: Annotated[bool, Opt('--show-confirmation', help='Shows the confirmation message box before items are emptied')] = False
    show_progress_ui: Annotated[bool, Opt('--show-progress-ui', help='Shows the progress dialog box as the Recycle Bin is being emptied')] = False
    play_sound: Annotated[bool, Opt('--play-sound', help='Plays the emptying sound on supported systems')] = False

    def _empty(self, flags: int):
        # TODO handle errors better
        try:
            SHEmptyRecycleBinW(None, None, flags)
            return True
        except OSError:
            return False

    def run(self, app):
        flags = 0

        if not self.show_confirmation:
            flags |= SHERB_NOCONFIRMATION

        if not self.show_progress_ui:
            flags |= SHERB_NOPROGRESSUI

        if not self.play_sound:
            flags |= SHERB_NOSOUND

        has_emptied = self._empty(flags)

        if self.format == 'plain':
            if has_emptied:
                self.writeln('Emptied the Recycle Bin')
            else:
                self.writeln('No items to empty out')
        else:
            self.writeln({
                'emptied': has_emptied,
            })

        return 0
