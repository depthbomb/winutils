from src.app import App
from subprocess import run
from datetime import datetime
from src.lib.ansi import link
from typing import Optional, TypedDict
from src.lib.utils import parse_csv_str
from src.commands.formattable import FormattableCommand

class HotFixRecord(TypedDict):
    Node: str
    Caption: Optional[str]
    CSName: str
    Description: Optional[str]
    FixComments: Optional[str]
    HotFixID: str
    InstallDate: Optional[str]
    InstalledBy: Optional[str]
    InstalledOn: Optional[str]
    Name: Optional[str]
    ServicePackInEffect: Optional[str]
    Status: Optional[str]

class UpdatesCommand(FormattableCommand):
    """
    Functions relating to Windows updates
    """
    def __init__(self):
        super().__init__()

    def _parse_date(self, value: str | None):
        if not value:
            return None

        try:
            return datetime.strptime(value, '%m/%d/%Y').date()
        except ValueError:
            return None

    def run(self, app: App):
        res = run(['wmic', 'qfe', 'list', '/format:csv'], text=True, capture_output=True, check=True)
        records = parse_csv_str(res.stdout)
        sorted_records = sorted(records, key=lambda r: self._parse_date(r['InstalledOn']) or datetime.max.date())
        max_desc_len = max((len(r['Description']) for r in sorted_records if r['Description']), default=0)

        for record in sorted_records:
            description = record['Description'].ljust(max_desc_len)
            hotfixid = link(record['HotFixID'], record['Caption']) if record['Caption'] is not None else record['HotFixID']
            self.writeln('%s\t\t%s\tInstalled on %s' % (
                description,
                hotfixid,
                record['InstalledOn']
            ))

        return 0
