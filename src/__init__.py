_g = globals()

APP_NAME = 'winutils'
APP_DISPLAY_NAME = 'WinUtils'
APP_DESCRIPTION = 'Utility CLI Application for Windows 10+'
APP_VERSION = (0, 2, 0, 0)
APP_ORG = 'Caprine Logic'
APP_USER_MODEL_ID = u'CaprineLogic.WinUtils'
APP_CLSID = '697A24DC-8E44-4F0F-8104-58E2730D8E00'
APP_VERSION_STRING = '.'.join(str(v) for v in APP_VERSION)
APP_REPO_OWNER = 'depthbomb'
APP_REPO_NAME = 'WinUtils'
APP_REPO_URL = f'https://github.com/{APP_REPO_OWNER}/{APP_REPO_NAME}'
APP_RELEASES_URL = f'https://github.com/{APP_REPO_OWNER}/{APP_REPO_NAME}/releases'
APP_LATEST_RELEASE_URL = f'https://github.com/{APP_REPO_OWNER}/{APP_REPO_NAME}/releases/latest'
APP_NEW_ISSUE_URL = f'https://github.com/{APP_REPO_OWNER}/{APP_REPO_NAME}/issues/new/choose'

__version__ = APP_VERSION_STRING

#region Flags
IS_COMPILED = '__compiled__' in _g
if IS_COMPILED:
    IS_STANDALONE = bool(_g['__compiled__'].standalone)
    IS_ONEFILE = bool(_g['__compiled__'].onefile)
else:
    IS_STANDALONE = False
    IS_ONEFILE = False
#endregion
