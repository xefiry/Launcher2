import tkinter as tk
from tkinter import ttk

from src.configuration import Config


class UI(tk.Tk):
    def __init__(self, config: 'Config') -> None:
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
        self.input.bind("<Key>", self.on_input_key)  # type: ignore

        self.list_active: int = 0
        self.list_var = tk.Variable()
        self.list = tk.Listbox(frm, listvariable=self.list_var)
        self.list.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        self.set_active(0)

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
        elif key == "Return":
            print(cur)
        elif key == "Tab":
            return "break"  # to do nothing when pressing tab
        elif event.char != "":  # type: ignore
            self.update_list()

    def set_active(self, new: int):
        self.list.selection_clear(self.list_active)
        self.list.selection_set(new)
        self.list.activate(new)

        self.list_active = new

    def update_list(self) -> None:
        print("update_list : ToDo")
