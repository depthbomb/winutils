from foxcli.cli import CLI
from src import APP_NAME, APP_VERSION_STRING

class App(CLI):
    def __init__(self):
        super().__init__(name=APP_NAME, version=APP_VERSION_STRING, description=APP_NAME)

app = App()
