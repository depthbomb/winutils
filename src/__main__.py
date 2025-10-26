from sys import exit
from src.app import App
from src import APP_NAME, APP_VERSION_STRING
from src.commands.temp import ClearTempCommand
from src.commands.updates import UpdatesCommand
from src.commands.disk_usage import DiskUsageCommand
from src.commands.spotlight_saver import SpotlightSaverCommand
from src.commands.recycle_bin import RecycleBinQueryCommand, RecycleBinEmptyCommand

app = App(name=APP_NAME, version=APP_VERSION_STRING, description=APP_NAME)
app.register(RecycleBinQueryCommand, path=['recycle-bin', 'query'])
app.register(RecycleBinEmptyCommand, path=['recycle-bin', 'empty'])
app.register(ClearTempCommand)
app.register(SpotlightSaverCommand)
app.register(UpdatesCommand)
app.register(DiskUsageCommand)

exit(app.run())
