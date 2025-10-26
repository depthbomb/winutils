from typing import Optional
from ctypes import WinDLL, c_byte, POINTER, HRESULT, c_void_p, wintypes, Structure, c_longlong

shell32 = WinDLL('shell32', use_last_error=True)
ole32 = WinDLL('ole32', use_last_error=True)

class GUID(Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', c_byte * 8),
    ]

    def __init__(self, guid: Optional[str] = None):
        super().__init__()
        if guid:
            from uuid import UUID
            u = UUID(guid)
            self.Data1 = u.time_low
            self.Data2 = u.time_mid
            self.Data3 = u.time_hi_version
            self.Data4[:] = u.bytes[8:]

#region Recycle Bin
class SHQUERYRBINFO(Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('i64Size', c_longlong),
        ('i64NumItems', c_longlong),
    ]

SHQueryRecycleBinW = shell32.SHQueryRecycleBinW
SHQueryRecycleBinW.argtypes = [wintypes.LPCWSTR, POINTER(SHQUERYRBINFO)]
SHQueryRecycleBinW.restype = HRESULT

SHEmptyRecycleBinW = shell32.SHEmptyRecycleBinW
SHEmptyRecycleBinW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.DWORD]
SHEmptyRecycleBinW.restype = HRESULT

SHERB_NOCONFIRMATION = 0x00000001
SHERB_NOPROGRESSUI = 0x00000002
SHERB_NOSOUND = 0x00000004
#endregion

#region Known Folders
REFKNOWNFOLDERID = c_void_p
LPWSTR = wintypes.LPWSTR

SHGetKnownFolderPath = shell32.SHGetKnownFolderPath
SHGetKnownFolderPath.argtypes = [REFKNOWNFOLDERID, wintypes.DWORD, wintypes.HANDLE, POINTER(LPWSTR)]
SHGetKnownFolderPath.restype = HRESULT

CoTaskMemFree = ole32.CoTaskMemFree
CoTaskMemFree.argtypes = [c_void_p]

# not exhaustive, cherry-picked from https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid
FOLDERID_Desktop = '{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}'
FOLDERID_Documents = '{FDD39AD0-238F-46AF-ADB4-6C85480369C7}'
FOLDERID_Downloads = '{374DE290-123F-4565-9164-39C4925E467B}'
FOLDERID_Music = '{4BD8D571-6D19-48D3-BE97-422220080E43}'
FOLDERID_Pictures = '{33E28130-4E1E-4676-835A-98395C3BC3BB}'
FOLDERID_Videos = '{18989B1D-99B5-455B-841C-AB7C74E4DDFC}'
#endregion
