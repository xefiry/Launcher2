import datetime as dt
import os
import subprocess
import tkinter as tk
import tomllib
from tkinter import messagebox as msg
from tkinter import ttk

import tomlkit

CONFIG_FILE = "config.toml"


class Config:
    def __init__(self, file_path: str) -> None:
        """Create configuration from toml file

        Args:
            file_path (str): The .toml file to use

        ToDo:
            better handle missing keys
        """

        with open(file_path, "rb") as file:
            data = tomllib.load(file)

        self.file_path: str = file_path
        self.search_description: bool = data["Config"]["search_description"]
        self.max_results: int = data["Config"]["max_results"]
        self.rules: list[Rule] = []

        if "Variables" in data:
            self.variables: dict[str, str] = data["Variables"]
            self.parse_variables()

        for d in data["Rule"]:
            self.rules.append(Rule(d))

    def __repr__(self) -> str:
        result: str = ""

        for r in self.rules:
            result += str(r) + "\n"

        return result

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {}

        result["Config"] = {
            "search_description": self.search_description,
            "max_results": self.max_results,
        }
        if hasattr(self, "variables"):
            result["Variables"] = self.variables
        result["Rule"] = [rule.__dict__ for rule in self.rules]

        return result

    def parse_variables(self):
        for key, var in self.variables.items():
            if type(var) is not str:
                msg.showwarning(  # type: ignore
                    "Wrong variable type",
                    f"Variable {key} is wrong type.\n"
                    + f"Expected {type('')}, got {str(type(var))}\n"
                    + "Key ignored.",
                )
            elif key in os.environ:
                msg.showwarning(  # type: ignore
                    "Wrong variable name",
                    f"An environment variable named '{key}' already exists.\n"
                    + "Key ignored.",
                )
            else:
                os.environ[key] = var

    def write(self) -> None:
        with open(self.file_path, "w") as f:
            tomlkit.dump(self.as_dict(), f)  # type: ignore

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
    def __init__(self, d: dict[str, str]) -> None:
        self.match: str = d["match"]
        self.description: str = d["description"]
        self.args: list[str] = list[str](d["args"])
        if "cwd" in d:
            self.cwd: str = d["cwd"]
        if "last_use" in d:
            self.last_use = dt.datetime.fromisoformat(str(d["last_use"]))

    def __repr__(self) -> str:
        mda: str = f"{self.match}' - '{self.description}' - {self.args}"
        cwd: str = f" - '{self.cwd}'" if hasattr(self, "cwd") else ""
        last_use: str = f" - '{self.last_use}'" if hasattr(self, "last_use") else ""

        return f"Rule('{mda}{cwd}{last_use})"

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
            ts0 = dt.datetime.fromtimestamp(0)
            a = self.last_use if hasattr(self, "last_use") else ts0
            b = value.last_use if hasattr(value, "last_use") else ts0
            return a < b
        else:
            return False

    def check(self, input: str) -> "Rule | None":
        if input.lower() in self.match.lower():
            return self
        else:
            return None

    @staticmethod
    def _process_path(path: str) -> str:
        result: str = path

        # expand as long as it changes the variable
        while result != os.path.expandvars(result):
            result = os.path.expandvars(result)

        result = os.path.normpath(result)

        return result

    def execute(self) -> None:
        cwd: str | None
        args: list[str] = []

        if hasattr(self, "cwd"):
            cwd = Rule._process_path(self.cwd)
        else:
            cwd = None

        for arg in self.args:
            args.append(Rule._process_path(arg))

        try:
            subprocess.Popen(args, cwd=cwd)
        except Exception as e:
            msg.showerror("Fatal error", str(e))  # type: ignore
            exit(-1)

        self.last_use = dt.datetime.now()


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
        self.input.bind("<Return>", lambda x: self.execute_rule())
        self.input.bind("<Escape>", lambda x: self.quit())
        self.input.bind("<Up>", lambda x: self.list.focus())
        self.input.bind("<Down>", lambda x: self.list.focus())

        self.scrollbar = ttk.Scrollbar(frm)
        self.scrollbar.pack(fill=tk.BOTH, side=tk.RIGHT)

        self.list_var = tk.Variable()
        self.list = tk.Listbox(frm, listvariable=self.list_var)
        self.list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.list.config(yscrollcommand=self.scrollbar.set)
        self.list.bind("<Return>", lambda x: self.execute_rule())
        self.list.bind("<Double-Button-1>", lambda x: self.execute_rule())

        self.list.bind("<Escape>", lambda x: self.quit())

        self.config = config
        self.update_list()

    def start(self) -> None:
        self.mainloop()

    def execute_rule(self) -> None:
        # get selected element in the list
        cur: tuple[int] = tuple[int](self.list.curselection())  # type: ignore

        # if there is not only one, do nothing (there can be 0)
        if len(cur) != 1:
            return

        n: int = cur[0]

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
        conf.write()
        ui = UI(conf)
        ui.mainloop()
    except Exception as e:
        msg.showerror("Fatal error", str(e))  # type: ignore


if __name__ == "__main__":
    run()
