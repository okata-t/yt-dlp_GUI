import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyperclip


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.fonts = ("游ゴシック", 15)
        self.title("yt-dlp_GUI")
        self.geometry("600x240")

        self.setup()

    def setup(self):
        self.ent_url = ctk.CTkEntry(
            self, width=400, placeholder_text="URL", font=self.fonts
        )
        self.ent_url.grid(row=0, column=0, padx=20, pady=10)

        self.btn_paste = ctk.CTkButton(
            self, width=100, text="ペースト", command=self.paste, font=self.fonts
        )
        self.btn_paste.grid(row=0, column=1, padx=20, pady=10)

        self.ent_savedir = ctk.CTkEntry(
            self, width=400, placeholder_text="保存先フォルダ", font=self.fonts
        )
        self.ent_savedir.grid(row=1, column=0, padx=20, pady=10)

        self.btn_savedir = ctk.CTkButton(
            self, width=100, text="参照", command=self.savedir, font=self.fonts
        )
        self.btn_savedir.grid(row=1, column=1, padx=20, pady=10)

        self.ent_filename = ctk.CTkEntry(
            self, placeholder_text="保存ファイル名", width=400, font=self.fonts
        )
        self.ent_filename.grid(row=2, column=0, padx=20, pady=10)

        self.btn_download = ctk.CTkButton(
            self, width=100, text="ダウンロード", command=self.download, font=self.fonts
        )
        self.btn_download.grid(row=2, column=1, padx=20, pady=10)

    def paste(self):
        clip_text = pyperclip.paste()
        self.ent_url.delete(0, tk.END)
        self.ent_url.insert(0, clip_text)

    def savedir(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = filedialog.askdirectory(initialdir=current_dir)
        self.ent_savedir.delete(0, tk.END)
        self.ent_savedir.insert(0, file_path)

    def download(self):
        messagebox.showinfo("ダウンロード", "まだ作ってないよ")


app = App()
app.mainloop()
