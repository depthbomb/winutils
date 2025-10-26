from foxcli.option import Opt
from os import linesep, PathLike
from foxcli.command import Command
from orjson import dumps, OPT_INDENT_2
from typing import Union, Literal, Annotated

type Formattable = Union[str, dict, list, PathLike]

class FormattableCommand(Command):
    format: Annotated[Literal['plain', 'json'], Opt('--format', choices=['plain', 'json'], help='Format to use when writing to stdout')] = 'plain'

    def write(self, data: Formattable) -> None:
        if self.format == 'json':
            self.stdout.write(dumps(data, option=OPT_INDENT_2).decode())
        else:
            self.stdout.write(str(data))

    def writeln(self, data: Formattable) -> None:
        if self.format == 'json':
            self.stdout.write(dumps(data, option=OPT_INDENT_2).decode() + linesep)
        else:
            self.stdout.write(str(data) + linesep)
