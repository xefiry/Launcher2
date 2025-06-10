import subprocess
import time
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk

import tomllib

CONFIG_FILE = "config.toml"


class Config:
    def __init__(self, file_path: str) -> None:
        """Create configuration from toml file

        Args:
            file_path (str): The .toml file to use

        ToDo:
            manage errors due to missing keys
        """

        with open(file_path, "rb") as file:
            data = tomllib.load(file)

        self.file_path: str = file_path
        self.search_description: bool = data["Config"]["search_description"]
        self.max_results: int = data["Config"]["max_results"]
        self.rules: list[Rule] = []

        for d in data["Rules"]:
            self.rules.append(Rule.from_dict(d))

    def __repr__(self) -> str:
        result: str = ""

        for r in self.rules:
            result += str(r) + "\n"

        return result

    def as_toml(self) -> str:
        result = f"""[Config]
  search_description = {str(self.search_description).lower()}
  max_results = {self.max_results}
"""
        for r in self.rules:
            result += r.as_toml()

        return result

    def write(self) -> None:
        with open(self.file_path, "w") as f:
            f.write(self.as_toml())

    def filter_rules(self, input: str) -> list["Rule"]:
        result: list["Rule"] = []

        # if input is empty, we return all the rules
        if input == "":
            result = self.rules
        else:
            for rule in self.rules:
                if rule.check(input) is not None:
                    result.append(rule)

        result.sort(reverse=True)

        return result


class Rule:
    def __init__(
        self, match: str, description: str, args: list[str], last_use: str = ""
    ) -> None:
        self.match: str = match
        self.description: str = description
        self.args: list[str] = args
        self.last_use: str = last_use

    @staticmethod
    def from_dict(d: dict[str, str | list[str]]) -> "Rule":
        match: str = str(d["match"])
        description: str = str(d["description"])
        args: list[str] = list[str](d["args"])
        try:
            last_use: str = str(d["last_use"])
        except KeyError:
            last_use: str = ""

        return Rule(match, description, args, last_use)

    def __repr__(self) -> str:
        return f"Rule('{self.match}' - '{self.description}' - {self.args})"

    def as_toml(self) -> str:
        result = f"""
[[Rules]]
  match = "{self.match}"
  description = "{self.description}"
  args = {self.args}
"""
        if self.last_use != "":
            result += f"""  last_use = {self.last_use}
"""
        return result

    def __eq__(self, value: object) -> bool:
        if type(value) is Rule:
            return (
                self.match == value.match
                and self.description == value.description
                and self.args == value.args
            )
        else:
            return False

    def __lt__(self, value: object) -> bool:
        if type(value) is Rule:
            return self.last_use < value.last_use
        else:
            return False

    def check(self, input: str) -> "Rule | None":
        if input.lower() in self.match.lower():
            return self
        else:
            return None

    def execute(self) -> None:
        self.last_use = time.strftime("%Y-%m-%dT%H:%M:%S")
        subprocess.Popen(self.args)


class UI(tk.Tk):
    def __init__(self, config: "Config") -> None:
        tk.Tk.__init__(self)

        self.title("Launcher")
        self.geometry("350x220")

        frm = ttk.Frame(self, padding=5)
        frm.config()
        frm.pack(fill=tk.BOTH, expand=True)

        self.input_var = tk.StringVar(self)
        self.input = ttk.Entry(frm, textvariable=self.input_var)
        self.input.pack(anchor=tk.N, fill=tk.X, expand=True)
        self.input.focus()
        self.input_var.trace_add("write", lambda a, b, c: self.update_list())
        self.input.bind("<Key>", self.on_input_key)  # type: ignore

        self.list_active: int = 0
        self.list_var = tk.Variable()
        self.list = tk.Listbox(frm, listvariable=self.list_var)
        self.list.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)

        self.config = config
        self.update_list()

    def start(self) -> None:
        self.mainloop()

    def on_input_key(self, event) -> None | str:  # type: ignore
        key = event.keysym  # type: ignore
        cur = self.list_active
        max = len(self.list_var.get())  # type: ignore

        if key == "Escape":
            self.quit()
        elif key == "Up" and cur > 0:
            self.set_active(cur - 1)
        elif key == "Down" and cur < max - 1:
            self.set_active(cur + 1)
        elif key == "Return" and len(self.rules) > 0:
            self.rules[cur].execute()
            self.config.write()
            self.withdraw()  # hide before quit to prevent focus loss for executed program
            self.quit()
        elif key == "Tab":
            return "break"  # to do nothing when pressing tab

    def set_active(self, new: int):
        self.list.selection_clear(self.list_active)
        self.list.selection_set(new)
        self.list.activate(new)

        self.list_active = new

    def update_list(self) -> None:
        self.rules = self.config.filter_rules(self.input_var.get())

        new_list: list[str] = [
            f"{rule.match} - {rule.description}" for rule in self.rules
        ]
        self.list_var.set(new_list)  # type: ignore

        self.set_active(0)


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
