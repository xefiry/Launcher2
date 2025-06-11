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
            result = [rule for rule in self.rules]
        else:
            result = [rule for rule in self.rules if rule.check(input) is not None]

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
        args = '", "'.join(self.args)
        args = args.replace("\\", "\\\\")
        result = f"""
[[Rules]]
  match = "{self.match}"
  description = "{self.description}"
  args = ["{args}"]
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
        try:
            subprocess.Popen(self.args)
            self.last_use = time.strftime("%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            msg.showerror("Error opening file", str(e))  # type: ignore
            exit(-1)


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
        self.input.pack(fill=tk.X, side=tk.TOP)
        self.input.focus()
        self.input_var.trace_add("write", lambda a, b, c: self.update_list())
        self.input.bind("<Return>", self.execute_rule)  # type: ignore
        self.input.bind("<Escape>", lambda x: self.quit())

        self.scrollbar = ttk.Scrollbar(frm)
        self.scrollbar.pack(fill=tk.BOTH, side=tk.RIGHT)

        self.list_var = tk.Variable()
        self.list = tk.Listbox(frm, listvariable=self.list_var)
        self.list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.list.config(yscrollcommand=self.scrollbar.set)
        self.list.bind("<Return>", self.execute_rule)  # type: ignore
        self.list.bind("<Double-Button-1>", self.execute_rule)  # type: ignore

        self.list.bind("<Escape>", lambda x: self.quit())

        self.config = config
        self.update_list()

    def start(self) -> None:
        self.mainloop()

    def execute_rule(self, event) -> None:  # type: ignore
        try:
            n: int = self.list.curselection()[0]  # type: ignore
        except Exception:
            return

        self.rules[n].execute()
        self.config.write()
        self.withdraw()  # hide before quit to prevent focus loss for executed program
        self.quit()

    def update_list(self) -> None:
        self.rules = self.config.filter_rules(self.input_var.get())

        new_list: list[str] = [
            f"{rule.match} - {rule.description}" for rule in self.rules
        ]
        self.list_var.set(new_list)  # type: ignore

        self.list.selection_clear(0, 99999)
        self.list.selection_set(0)
        self.list.activate(0)


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
