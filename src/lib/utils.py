from io import StringIO
from csv import DictReader
from typing import TypedDict

def human_size(num_bytes: int, /, precision: int = 2) -> str:
    if not isinstance(num_bytes, int):
        raise TypeError(f'num_bytes must be int, not {type(num_bytes).__name__}')

    if num_bytes < 0:
        raise ValueError('num_bytes must be non-negative')

    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')
    size = float(num_bytes)
    unit = units[0]
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            break
        size /= 1024.0

    return f'{size:.{precision}f} {unit}'

def parse_csv_str(csv: str) -> list[TypedDict]:
    cleaned = csv.strip().replace('\r\n', '\n')
    reader = DictReader(StringIO(cleaned))
    records = []

    for row in reader:
        if not any(row.values()):
            continue

        clean_row = {
            k: (v.strip() if isinstance(v, str) else None) or None
            for k, v in row.items()
        }
        records.append(clean_row)

    return records

def format_hr_result(hr: int):
    return f'0x{(hr & 0xFFFFFFFF):08x}'
