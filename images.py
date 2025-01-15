import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox

def load_image(window, path, x=0, y=0, height=None, width=None, on_top=True):
    try:
        img = Image.open(path)

        # Resize the image if width and height are provided
        if width and height:
            img = img.resize((width, height), Image.LANCZOS)

        bck_img = ImageTk.PhotoImage(img)
        label = tk.Label(window, image=bck_img)
        label.image = bck_img
        label.place(x=x, y=y)
        if on_top:
            label.lift()
        else:
            label.lower()
        return label
    except Exception as e:
        messagebox.showerror("Error loading image", f"Error loading image: {e}")
        return None
