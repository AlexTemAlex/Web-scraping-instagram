import tkinter as tk
from tkinter import filedialog
import os

def seleccionar_json():
    if not os.path.exists("data"):
        os.makedirs("data")

    root = tk.Tk()
    root.withdraw()

    ruta = filedialog.askopenfilename(
        initialdir=os.path.abspath("data"),
        title="Seleccionar JSON",
        filetypes=[("JSON", "*.json")]
    )

    root.destroy()
    return ruta