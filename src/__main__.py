from src.configuration import Config
from src.ui import UI

CONFIG_FILE = "config.toml"


def run():
    conf = Config(CONFIG_FILE)

    ui = UI(conf)
    ui.mainloop()


if __name__ == "__main__":
    run()
