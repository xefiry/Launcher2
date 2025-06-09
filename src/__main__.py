from src.configuration import Config
from src.ui import UI

CONFIG_FILE = "config.toml"


def run():
    conf = Config(CONFIG_FILE)
    print(conf)
    # conf.write()

    ui = UI()
    ui.mainloop()


if __name__ == "__main__":
    run()
