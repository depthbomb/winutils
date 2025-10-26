from functools import cache

ESC = '\u001B['
OSC = '\u001B]'
BEL = '\u0007'
SEP = ';'
RESET = f'{ESC}0m'

STYLES = {
    'bold': 1,
    'dim': 2,
    'italic': 3,
    'underline': 4,
    'blink_slow': 5,
    'blink_fast': 6,
    'reverse': 7,
    'hidden': 8,
    'strike': 9,
}

def _ansi_effects(*effects: str) -> str:
    codes = [str(STYLES[e]) for e in effects if e in STYLES]
    if not codes:
        return ''

    return f'{ESC}{SEP.join(codes)}m'

@cache
def _hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    hex_code = hex_code.lstrip('#')
    if len(hex_code) != 6:
        raise ValueError('Hex color must be 6 digits, e.g. #ff00ff')

    r, g, b = hex_code[:2], hex_code[2:4], hex_code[4:6]

    return int(r, 16), int(g, 16), int(b, 16)

@cache
def fg(color: int | tuple[int, int, int] | str) -> str:
    if isinstance(color, str):
        color = _hex_to_rgb(color)

    if isinstance(color, int):
        return f'{ESC}38{SEP}5{SEP}{color}m'

    r, g, b = color

    return f'{ESC}38{SEP}2{SEP}{r}{SEP}{g}{SEP}{b}m'

@cache
def bg(color: int | tuple[int, int, int] | str) -> str:
    if isinstance(color, str):
        color = _hex_to_rgb(color)

    if isinstance(color, int):
        return f'{ESC}48{SEP}5{SEP}{color}m'

    r, g, b = color

    return f'{ESC}48{SEP}2{SEP}{r}{SEP}{g}{SEP}{b}m'

def style(text: str, *effects: str) -> str:
    return f'{_ansi_effects(*effects)}{text}{RESET if effects else ''}'

def colorize(text: str, fg_color=None, bg_color=None, *effects: str) -> str:
    parts = []
    if fg_color is not None:
        parts.append(fg(fg_color))

    if bg_color is not None:
        parts.append(bg(bg_color))

    if effects:
        parts.append(_ansi_effects(*effects))

    return ''.join(parts) + text + RESET

def link(text: str, url: str, *effects: str) -> str:
    styled_text = f'{_ansi_effects(*effects)}{text}{RESET if effects else ''}'
    return ''.join([
        OSC,
        '8',
        SEP,
        SEP,
        url,
        BEL,
        styled_text,
        OSC,
        '8',
        SEP,
        SEP,
        BEL
    ])
