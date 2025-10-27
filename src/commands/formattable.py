from typing import Union
from foxcli.option import Opt
from os import linesep, PathLike
from foxcli.command import Command
from orjson import dumps, OPT_INDENT_2

type Formattable = Union[str, dict, list, PathLike]

class FormattableCommand(Command):
    options = [
        Opt('format', default='plain', help='Format to use when writing to stdout')
    ]

    def writeln(self, data: Formattable):
        if self.ctx.args.get('format', str) == 'json':
            self.ctx.stdout.write(dumps(data, option=OPT_INDENT_2).decode() + linesep)
        else:
            self.ctx.stdout.write(str(data) + linesep)
