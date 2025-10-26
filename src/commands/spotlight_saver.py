from os import getenv
from shutil import copy
from src.app import App
from pathlib import Path
from struct import unpack
from sys import executable
from typing import Annotated
from foxcli.option import Opt
from src.lib.types import TriBool
from ctypes import byref, wintypes
from foxcli.command import Command
from src.lib.native import GUID, CoTaskMemFree, FOLDERID_Pictures, SHGetKnownFolderPath

class SpotlightSaverCommand(Command):
    """
    Saves the Windows Spotlight lockscreen images to "Pictures\\Windows Spotlight"
    """
    startup: Annotated[bool, Opt('--startup', help='Toggle executing this command on startup, then exits')] = False

    def __init__(self):
        super().__init__()

        self.saved_images = 0

    def _get_image_resolution(self, path: Path) -> tuple[int, int]:
        """
        Returns the resolution of an image from its Path. The Spotlight images are JPEGs so we parse the data based on
        that.
        """
        with path.open('rb') as f:
            f.seek(0)
            while True:
                byte = f.read(1)
                while byte and ord(byte) != 0xFF:
                    byte = f.read(1)

                while byte == b'\xFF':
                    byte = f.read(1)

                if not byte:
                    break

                marker = ord(byte)
                if marker in [0xD8, 0x01]:
                    continue
                elif 0xD0 <= marker <= 0xD9:
                    continue
                else:
                    length = unpack('>H', f.read(2))[0]
                    if 0xC0 <= marker <= 0xC3:
                        f.read(1)
                        height, width = unpack('>HH', f.read(4))
                        return width, height
                    f.seek(length < 2, 1)

        return 0, 0

    def _get_known_folder_path(self, guid_str: str) -> Path:
        """
        Returns a Windows KnownFolder as a Path from its GUID.
        """
        guid = GUID(guid_str)
        pPath = wintypes.LPWSTR()
        hr = SHGetKnownFolderPath(byref(guid), 0, None, byref(pPath))

        try:
            return Path(pPath.value)
        finally:
            CoTaskMemFree(pPath)

    def _toggle_startup(self) -> TriBool:
        """
        Toggles whether the `spotlight-saver` command should be called on login. Returns `True` if it has been set to
        run on login, `False` if it has been removed from login, and `None` if there was an error performing either
        operation.
        """
        from src import IS_COMPILED

        if not IS_COMPILED:
            self.stdout.write('\nStartup can only be toggle when the app is compiled')
            return None

        from winreg import (
            REG_SZ,
            OpenKey,
            KEY_READ,
            SetValueEx,
            DeleteValue,
            QueryValueEx,
            KEY_SET_VALUE,
            HKEY_CURRENT_USER
        )

        key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        exe_path = str(Path(executable).parent / 'winutils.exe') + ' spotlight-saver'
        name = 'SpotlightSaver'

        try:
            with OpenKey(HKEY_CURRENT_USER, key_path, 0, KEY_READ | KEY_SET_VALUE) as key:
                try:
                    existing, _ = QueryValueEx(key, name)
                    if existing == exe_path:
                        DeleteValue(key, name)
                        return False
                    else:
                        SetValueEx(key, name, 0, REG_SZ, exe_path)
                        return True
                except FileNotFoundError:
                    SetValueEx(key, name, 0, REG_SZ, exe_path)
                    return True
        except Exception as e:
            return None

    def run(self, app: App):
        if self.startup:
            startup_enabled = self._toggle_startup()
            if startup_enabled:
                self.stdout.write('\nStartup enabled')
            elif not startup_enabled:
                self.stdout.write('\nStartup disabled')
            else:
                self.stdout.write('\nStartup could not be toggled')
            return 0

        assets_path = Path(getenv('LOCALAPPDATA')) / 'Packages' / 'Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy' / 'LocalState' / 'Assets'
        output_path = self._get_known_folder_path(FOLDERID_Pictures) / 'Windows Spotlight'
        output_path.mkdir(exist_ok=True)

        for path in assets_path.glob('*'):
            [width, height] = self._get_image_resolution(path)
            if width != 1920 or height != 1080:
                continue

            saved_path = output_path / (path.name + '.jpg')
            if saved_path.exists():
                continue

            copy(path, saved_path)

            self.saved_images += 1

        return 0
