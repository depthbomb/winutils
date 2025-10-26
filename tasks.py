from datetime import datetime
from invoke import task, Context
from src import (
    APP_ORG,
    APP_NAME,
    APP_CLSID,
    APP_REPO_URL,
    APP_DESCRIPTION,
    APP_RELEASES_URL,
    APP_DISPLAY_NAME,
    APP_NEW_ISSUE_URL,
    APP_USER_MODEL_ID,
    APP_VERSION_STRING
)

@task
def build(c: Context, onefile=False):
    args = [
        'nuitka',
        'src',
        f'--output-dir=build --output-filename={APP_NAME}',
        '--enable-plugin=upx',
        '--onefile-no-compression',
        '--windows-icon-from-ico=resources/icon.ico',
        f'--company-name="{APP_ORG}" --product-name="{APP_DISPLAY_NAME}" --product-version={APP_VERSION_STRING} --file-description="{APP_DISPLAY_NAME} - {APP_DESCRIPTION}" --copyright="Copyright (c) 2025 {APP_ORG}"',
    ]

    if onefile:
        args.append('--onefile')
    else:
        args.append('--standalone')

    c.run(' '.join(args))

@task
def create_setup(c: Context):
    definitions = {
        'NameLong': APP_DISPLAY_NAME,
        'Version': APP_VERSION_STRING,
        'Description': APP_DESCRIPTION,
        'Company': APP_ORG,
        'ExeName': f'{APP_NAME}.exe',
        'AppUserModelId': APP_USER_MODEL_ID,
        'AppUserModelToastActivatorClsid': APP_CLSID,
        'Copyright': f'Copyright (c) {datetime.now().year} {APP_ORG}',
        'RepoUrl': APP_REPO_URL,
        'ReleasesUrl': APP_RELEASES_URL,
        'IssuesUrl': APP_NEW_ISSUE_URL
    }
    cmd = ' '.join([
        'iscc.exe',
        'setup/setup.iss',
        ' '.join([f"/d{key}=\"{value}\"" for key, value in definitions.items()])
    ])
    c.run(cmd)
