import configparser
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyperclip
import yt_dlp


class App(ctk.CTk):
    config = configparser.ConfigParser()
    ini_path = "config.ini"

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.fonts = ("游ゴシック", 15)
        self.title("yt-dlp_GUI")
        self.geometry("600x240")

        self.read_config()
        self.setup()
        self.opt = {
            "progress_hooks": [self.hook],
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        }

    def read_config(self):
        if not os.path.exists(self.ini_path):
            with open(self.ini_path, "w") as f:
                self.config["Directory"] = {}
                self.config["Directory"]["lastdir"] = "./"
                self.config.write(f)
        self.config.read(self.ini_path, encoding="shift-jis")

    def write_config(self, section, key, value):
        self.config.set(section, key, str(value))
        with open(self.ini_path, "w") as f:
            self.config.write(f)

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
            self,
            placeholder_text="保存ファイル名(空白ならタイトル)",
            width=400,
            font=self.fonts,
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
        inidir = self.config["Directory"]["lastdir"]
        file_path = filedialog.askdirectory(initialdir=inidir)
        self.write_config("Directory", "lastdir", file_path)
        self.ent_savedir.delete(0, tk.END)
        self.ent_savedir.insert(0, file_path)

    def download(self):
        self.download_finished = 0
        file_path = self.ent_savedir.get()
        file_name = self.ent_filename.get()
        url = self.ent_url.get()

        if url == "":
            messagebox.showerror("エラー", "URLを入力してください")
            return
        if file_path == "":
            messagebox.showerror("エラー", "保存フォルダを指定してください")
            return
        if file_name == "":
            file_name = "%(title)s"

        self.opt["outtmpl"] = file_path + "/" + file_name + ".%(ext)s"
        self.download_audio = False

        with yt_dlp.YoutubeDL(self.opt) as ydl:
            ydl.download([url])

    def hook(self, d):
        if d["status"] == "finished":
            self.download_finished += 1
            if self.download_finished >= (1 if self.download_audio else 2):
                messagebox.showinfo("完了", "ダウンロードが完了しました")


app = App()
app.mainloop()
