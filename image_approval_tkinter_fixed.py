import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import shutil

INPUT_FOLDER = "pending_review"
APPROVED_FOLDER = "approved"
REJECTED_FOLDER = "rejected"

# Creează foldere dacă nu există
os.makedirs(APPROVED_FOLDER, exist_ok=True)
os.makedirs(REJECTED_FOLDER, exist_ok=True)

# Lista imaginilor de aprobat
images = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
images.sort()

current_index = 0

def show_image(index):
    global img_display
    file = images[index]
    path = os.path.join(INPUT_FOLDER, file)
    code_var.set(f"Cod produs: {os.path.splitext(file)[0]}")

    img = Image.open(path)
    img = img.resize((400, 400), Image.LANCZOS)
    img_display = ImageTk.PhotoImage(img)
    image_label.config(image=img_display)

def approve():
    file = images[current_index]
    shutil.move(os.path.join(INPUT_FOLDER, file), os.path.join(APPROVED_FOLDER, file))
    next_image()

def reject():
    file = images[current_index]
    shutil.move(os.path.join(INPUT_FOLDER, file), os.path.join(REJECTED_FOLDER, file))
    next_image()

def next_image():
    global current_index
    current_index += 1
    if current_index < len(images):
        show_image(current_index)
    else:
        messagebox.showinfo("Gata!", "Ai terminat de aprobat toate imaginile.")
        root.quit()

# Construire UI
root = tk.Tk()
root.title("Aprobă imagini pentru produse")
code_var = tk.StringVar()

tk.Label(root, textvariable=code_var, font=("Arial", 16)).pack(pady=10)
image_label = tk.Label(root)
image_label.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="✅ Aprobat", width=15, command=approve).pack(side="left", padx=10)
tk.Button(btn_frame, text="❌ Respins", width=15, command=reject).pack(side="right", padx=10)

if images:
    show_image(current_index)
else:
    messagebox.showinfo("Nimic de aprobat", "Folderul pending_review este gol.")
    root.destroy()

root.mainloop()
