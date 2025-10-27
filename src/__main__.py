from sys import exit
from src.app import app

import src.commands.disk_usage
import src.commands.recycle_bin
import src.commands.spotlight_saver
import src.commands.temp
import src.commands.updates

exit(app.run())
