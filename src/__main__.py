from src.configuration import Config

CONFIG_FILE = "config.toml"


def run():
    conf = Config(CONFIG_FILE)
    print(conf)
    # conf.write()


if __name__ == "__main__":
    run()
