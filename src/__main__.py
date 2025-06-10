from tkinter import messagebox as msg

from src.configuration import Config
from src.ui import UI

CONFIG_FILE = "config.toml"


def run():
    try:
        conf = Config(CONFIG_FILE)
        ui = UI(conf)
        ui.mainloop()
    except Exception as e:
        msg.showerror("Error opening file", str(e))  # type: ignore
        exit(-1)


if __name__ == "__main__":
    run()
