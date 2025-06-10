import tkinter as tk
from tkinter import ttk


class UI(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)

        self.title("Launcher")
        self.geometry("350x220")

        self.input_var = tk.StringVar(self)
        self.list_var = tk.Variable(value=["Zero", "One", "Two"])

        frm = ttk.Frame(self, padding=5)
        frm.config()
        frm.pack(fill=tk.BOTH, expand=True)

        self.input = ttk.Entry(frm, textvariable=self.input_var)
        self.input.pack(anchor=tk.N, fill=tk.X, expand=True)
        self.input.focus()

        self.input.bind("<Key>", self.on_input_change)  # type: ignore
        self.input.bind("<Return>", self.on_input_enter)  # type: ignore

        self.list = tk.Listbox(frm, listvariable=self.list_var)
        self.list.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        self.list.selection_set(0)
        self.list.activate(0)

    def start(self) -> None:
        self.mainloop()

    def on_input_change(self, event) -> None:  # type: ignore
        key = event.keysym  # type: ignore
        cur = int(self.list.curselection()[0])  # type: ignore
        max = len(self.list_var.get())  # type: ignore

        if key == "Up":
            if cur > 0:
                self.list.selection_clear(cur)
                self.list.selection_set(cur - 1)
                self.list.activate(cur - 1)
        elif key == "Down":
            if cur < max - 1:
                self.list.selection_clear(cur)
                self.list.selection_set(cur + 1)
                self.list.activate(cur + 1)
        elif key == "Escape":
            self.quit()
        else:
            print(event)  # type: ignore

    def on_input_enter(self, event) -> None:  # type: ignore
        cur = int(self.list.curselection()[0])  # type: ignore
        val = str(self.list_var.get()[cur])  # type: ignore
        print(cur)
        print(val)
