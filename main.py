import configparser
import datetime
import math
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog

import CTkMenuBar
import CTkMessagebox
import customtkinter as ctk
import darkdetect
import pyperclip
import requests
import yt_dlp
from bs4 import BeautifulSoup
from packaging import version
from win11toast import toast


class App(ctk.CTk):
    config = configparser.ConfigParser(interpolation=None)
    ini_path = "config.ini"

    def __init__(self):
        super().__init__()

        # Windowsのテーマ色設定。"Light" or "Dark"
        self.color_mode = darkdetect.theme()

        ver = configparser.ConfigParser()
        ver.read("version.ini", encoding="shift-jis")
        this_version = ver["Version"]["version"]

        ctk.set_appearance_mode(self.color_mode)
        ctk.set_default_color_theme("blue")
        self.fonts = ("游ゴシック", 15)
        self.title("yt-dlp_GUI " + this_version)
        self.geometry("900x300")
        self.iconbitmap("icon.ico")

        self.create_menu()
        self.read_config()
        self.setup()
        self.load_option()
        self.check_version(this_version)
        self.check_option()

    def check_version(self, this_version):
        r = requests.get(
            "https://api.github.com/repos/okata-t/yt-dlp_GUI/releases/latest"
        )

        # API呼び出し上限の場合、スクレイピングしてバージョンを取得
        try:
            latest_version = r.json()["tag_name"]
        except KeyError:
            url = "https://github.com/okata-t/yt-dlp_GUI/releases/latest"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            latest_version = soup.find(class_="d-inline mr-3").text[11:]

        if version.parse(this_version) < version.parse(latest_version):
            msg = CTkMessagebox.CTkMessagebox(
                title="アップデート",
                message="新しいバージョン："
                + latest_version
                + "\nが公開されました。\nダウンロードしますか？",
                icon="info",
                font=self.fonts,
                option_1="キャンセル",
                option_2="ダウンロード",
                option_3="GitHubへ",
            )
            if msg.get() == "GitHubへ":
                subprocess.run(
                    "start https://github.com/okata-t/yt-dlp_GUI/releases/latest",
                    shell=True,
                )
                sys.exit()
            elif msg.get() == "ダウンロード":
                subprocess.run(
                    "start https://github.com/okata-t/yt-dlp_GUI/releases/latest/"
                    + "download/yt-dlp_GUI_Setup.exe",
                    shell=True,
                )
                sys.exit()

    def uninstall(self):
        os.remove("config.ini")
        cp = subprocess.run("start unins000.exe", shell=True)
        if cp.returncode == 0:
            sys.exit()

    # メニューバーを追加
    def create_menu(self):
        if self.color_mode == "Dark":
            self.color_menubar = "#242424"
            self.color_edit = "#EBEBEB"
        else:
            self.color_menubar = "#EBEBEB"
            self.color_edit = "#242424"
        menu = CTkMenuBar.CTkMenuBar(self, bg_color=self.color_menubar)
        self.pack_propagate(0)
        # File menu
        file_menu = menu.add_cascade("オプション", font=self.fonts)
        file_dropdown = CTkMenuBar.CustomDropdownMenu(file_menu, font=self.fonts)
        file_dropdown.add_option(
            "YouTubeを開く",
            command=lambda: subprocess.run("start https://youtube.com", shell=True),
        )
        file_dropdown.add_option(
            "アンインストール",
            command=lambda: self.uninstall(),
        )
        file_dropdown.add_separator()

        # メニューバーのテンプレート
        """
        export_submenu = file_dropdown.add_submenu("Export As")
        export_submenu.add_option(".TXT")
        export_submenu.add_option(".PDF")

        # Edit menu
        edit_menu = menu.add_cascade("Edit")
        edit_dropdown = CustomDropdownMenu(edit_menu)
        edit_dropdown.add_option("Cut")
        edit_dropdown.add_option("Copy")
        edit_dropdown.add_option("Paste")

        # Settings menu
        settings_menu = menu.add_cascade("Settings")
        settings_dropdown = CustomDropdownMenu(settings_menu)
        settings_dropdown.add_option("Preferences")
        settings_dropdown.add_option("Update")

        # About menu
        about_menu = menu.add_cascade("About")
        about_dropdown = CustomDropdownMenu(about_menu)
        about_dropdown.add_option("Hello World")
        """

    def read_config(self):
        if not os.path.exists(self.ini_path):
            self.init_config()
        self.config.read(self.ini_path, encoding="shift-jis")

    def write_config(self):
        with open(self.ini_path, "w") as f:
            self.config["Directory"]["lastdir"] = self.ent_savedir.get()
            self.config["Directory"]["filename"] = self.ent_filename.get()
            self.config["Option"] = {}
            self.config["Option"]["download_audio"] = str(self.chk_audio.get())
            self.config["Option"]["embed_thumbnail"] = str(self.chk_thumbnail.get())
            self.config["Option"]["extension"] = str(self.cmb_extension.get())
            self.config.write(f)
        self.destroy()

    def load_option(self):
        try:
            self.var_chk_audio.set(self.config["Option"]["download_audio"])
            self.var_chk_thumbnail.set(self.config["Option"]["embed_thumbnail"])
            self.cmb_extension.set(self.config["Option"]["extension"])
        except KeyError as error_message:
            a = str(error_message)
            with open(self.ini_path, "w") as f:
                self.config["Option"][a[1:-1]] = ""
                self.config.write(f)

    def init_config(self):
        # Downloadsフォルダのパスを取得
        user_folder = os.path.expanduser("~")
        download_path = os.path.join(user_folder, "Downloads")

        with open(self.ini_path, "w") as f:
            self.config["Directory"] = {}
            self.config["Directory"]["lastdir"] = download_path
            self.config["Directory"]["filename"] = ""
            self.config["Option"] = {}
            self.config["Option"]["download_audio"] = "0"
            self.config["Option"]["embed_thumbnail"] = "0"
            self.config["Option"]["extension"] = "mp4"
            self.config.write(f)

    def check_option(self, *args):
        if self.var_chk_audio.get():
            self.cmb_extension.configure(values=self.dict_file["audio"])
            if self.cmb_extension.get() == "wav":
                self.var_chk_thumbnail.set(False)
                self.chk_thumbnail.configure(state="disabled")
            else:
                self.chk_thumbnail.configure(state="normal")
        else:
            self.cmb_extension.configure(values=self.dict_file["movie"])
            self.chk_thumbnail.configure(state="normal")

    def change_extension(self, mode):
        if self.var_chk_audio.get():

            self.cmb_extension.set(self.dict_file["audio"][0])
        else:
            self.cmb_extension.set(self.dict_file["movie"][0])

    def setup(self):
        self.toplevel_window = None
        self.frame_main = ctk.CTkFrame(self, width=540)
        self.frame_main.grid(row=0, column=0, padx=10, pady=35, sticky="nsew")

        self.frame_option = ctk.CTkFrame(self, width=360)
        self.frame_option.grid(row=0, column=1, padx=10, pady=35, sticky="nsew")

        self.frame_progress = ctk.CTkFrame(self, width=920)
        self.frame_progress.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.frame_main.columnconfigure(1, weight=1)
        self.frame_progress.columnconfigure(0, weight=1)

        self.ent_url = ctk.CTkEntry(
            self.frame_main, width=400, placeholder_text="URL", font=self.fonts
        )
        self.ent_url.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.btn_paste = ctk.CTkButton(
            self.frame_main,
            width=100,
            text="ペースト",
            command=self.paste,
            font=self.fonts,
        )
        self.btn_paste.grid(
            row=0,
            column=2,
            padx=10,
            pady=10,
        )

        self.ent_savedir = ctk.CTkEntry(
            self.frame_main,
            width=400,
            placeholder_text="保存先フォルダ",
            font=self.fonts,
        )
        self.ent_savedir.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        if self.config["Directory"]["lastdir"] != "":
            self.ent_savedir.insert(0, self.config["Directory"]["lastdir"])

        self.btn_savedir = ctk.CTkButton(
            self.frame_main,
            width=100,
            text="参照",
            command=self.savedir,
            font=self.fonts,
        )
        self.btn_savedir.grid(row=1, column=2, padx=10, pady=10)

        self.btn_editname = ctk.CTkButton(
            self.frame_main,
            width=10,
            text="編集",
            font=self.fonts,
            text_color=self.color_edit,
            fg_color="transparent",
            border_width=2.5,
            command=self.edit_filename,
        )
        self.btn_editname.grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
        )

        self.ent_filename = ctk.CTkEntry(
            self.frame_main,
            placeholder_text="保存ファイル名(空白ならタイトル)",
            width=340,
            font=self.fonts,
        )
        self.ent_filename.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        if self.config["Directory"]["filename"] != "":
            self.ent_filename.insert(0, self.config["Directory"]["filename"])

        self.btn_download = ctk.CTkButton(
            self.frame_main,
            width=100,
            text="ダウンロード",
            command=self.start_download,
            font=self.fonts,
        )
        self.btn_download.grid(row=2, column=2, padx=10, pady=10)

        self.lbl_progress = ctk.CTkLabel(self.frame_progress, text="", font=self.fonts)
        self.lbl_progress.grid(row=0, column=0, padx=10, sticky="w")

        self.lbl_eta = ctk.CTkLabel(self.frame_progress, text="", font=self.fonts)
        self.lbl_eta.grid(row=0, column=1, padx=10, sticky="e")

        self.pbar_progress = ctk.CTkProgressBar(self.frame_progress, width=920)
        self.pbar_progress.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        self.pbar_progress.set(0)

        self.var_chk_audio = ctk.BooleanVar()
        self.chk_audio = ctk.CTkCheckBox(
            self.frame_option,
            text="音声のみダウンロード",
            font=self.fonts,
            command=lambda: [
                self.check_option(),
                self.change_extension(self.var_chk_audio),
            ],
            variable=self.var_chk_audio,
        )
        self.chk_audio.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.var_chk_thumbnail = ctk.BooleanVar()
        self.chk_thumbnail = ctk.CTkCheckBox(
            self.frame_option,
            text="サムネイルを埋め込む",
            font=self.fonts,
            variable=self.var_chk_thumbnail,
        )
        self.chk_thumbnail.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.dict_file = {
            "movie": ["mp4", "webm"],
            "audio": ["mp3", "wav", "m4a", "opus"],
        }

        self.cmb_extension = ctk.CTkComboBox(
            self.frame_option,
            values=self.dict_file["movie"],
            font=self.fonts,
            width=100,
            command=self.check_option,
        )
        self.cmb_extension.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    def paste(self):
        clip_text = pyperclip.paste()
        self.ent_url.delete(0, tk.END)
        self.ent_url.insert(0, clip_text)

    def savedir(self):
        inidir = self.config["Directory"]["lastdir"]
        file_path = filedialog.askdirectory(initialdir=inidir)
        self.ent_savedir.delete(0, tk.END)
        self.ent_savedir.insert(0, file_path)

    def start_download(self):
        self.opt = {
            "progress_hooks": [self.progress_hook],
            "postprocessor_hooks": [self.postprocessor_hook],
            "postprocessors": [],
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        }
        file_path = self.ent_savedir.get()
        file_name = self.ent_filename.get()
        url = self.ent_url.get()

        if url == "":
            CTkMessagebox.CTkMessagebox(
                title="エラー",
                message="URLを入力してください",
                icon="cancel",
                font=self.fonts,
            )
            return
        if file_path == "":
            CTkMessagebox.CTkMessagebox(
                title="エラー",
                message="保存フォルダを指定してください",
                icon="cancel",
                font=self.fonts,
            )
            return
        if file_name == "":
            file_name = "%(title)s"

        extension = self.cmb_extension.get()
        download_audio = self.chk_audio.get()
        embed_thumbnail = self.chk_thumbnail.get()

        if extension == "webm":
            self.opt["format"] = "best[ext=webm]/bestvideo+bestaudio/best[ext=mp4]"
            self.opt["postprocessors"].append(
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "webm",
                }
            )

        if download_audio:
            self.opt["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": extension,
                }
            )
            self.opt["format"] = "bestaudio/best"

        if embed_thumbnail:
            self.opt["writethumbnail"] = True
            self.opt["postprocessors"].append({"key": "EmbedThumbnail"})
        self.opt["outtmpl"] = file_path + "/" + file_name + ".%(ext)s"
        self.download_finished = 1 if download_audio else 2
        self.thread = threading.Thread(target=self.download, args=(url,))
        self.thread.start()

    def download(self, url):
        self.pbar_progress.set(0)
        self.lbl_progress.configure(text="準備中")
        self.lbl_eta.configure(text="")
        with yt_dlp.YoutubeDL(self.opt) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                CTkMessagebox.CTkMessagebox(
                    title="エラーが発生しました",
                    message=e,
                    icon="cancel",
                    font=self.fonts,
                )

    def progress_hook(self, d):
        if d["status"] == "downloading":
            self.set_progress(
                self.download_finished,
                d.get("downloaded_bytes", None),
                d.get("total_bytes_estimate", None),
                d.get("speed", None),
                d.get("eta", None),
            )

        elif d["status"] == "finished":
            self.download_finished -= 1

    def set_progress(self, downloading, downloaded_bytes, total_bytes, speed, eta):
        if downloading == 2:
            downloading_text = "動画"
        else:
            downloading_text = "音声"

        if total_bytes is None:
            total_bytes = downloaded_bytes

        self.lbl_progress.configure(
            text=(
                downloading_text
                + "をダウンロード中："
                + str(round((downloaded_bytes / total_bytes * 100), 1))
                + "% / "
                + self.convert_size(total_bytes)
                + " ("
                + (self.convert_size(speed) if speed is not None else "...")
                + "/s)"
            )
        )
        if eta is None:
            eta = "..."
        else:
            eta = str(datetime.timedelta(seconds=round(float(eta))))
        self.lbl_eta.configure(text="残り " + eta)
        self.pbar_progress.set(downloaded_bytes / total_bytes)

    def convert_size(self, size):
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
        i = math.floor(math.log(size, 1024)) if size > 0 else 0
        size = round(size / 1024**i, 2)
        return f"{size} {units[i]}"

    def postprocessor_hook(self, d):
        if d["status"] == "started":
            self.lbl_progress.configure(text="処理中")
            self.lbl_eta.configure(text="")

        elif d["status"] == "finished":
            if d["postprocessor"] == "MoveFiles":
                self.lbl_progress.configure(text="ダウンロード完了")
                self.lbl_eta.configure(text="")
                toast("yt-dlp_GUI", "ダウンロードが完了しました")

    def edit_filename(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = EditFilename(self)
        else:
            self.toplevel_window.focus()


class EditFilename(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.fonts = ("游ゴシック", 15)
        self.title("ファイル名テンプレートの編集")
        self.geometry("740x240")
        self.after(100, self.focus)

        self.dict = {
            "ID": "id",
            "タイトル": "title",
            "URL": "url",
            "投稿者": "uploader",
            "投稿者ID": "uploader_id",
            "投稿日": "upload_date",
            "動画サイズ縦": "width",
            "動画サイズ横": "height",
            "FPS": "fps",
            "サイトドメイン": "extractor",
            "プレイリスト名": "playlist",
            "プレイリスト内番号": "playlist_index",
        }

        self.frame_entry = ctk.CTkFrame(self)
        self.frame_entry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_option = ctk.CTkFrame(self, width=600)
        self.frame_option.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.frame_entry.columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.frame_entry, font=self.fonts)
        self.entry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.load_text()

        self.apply = ctk.CTkButton(
            self.frame_entry,
            font=self.fonts,
            text="適用",
            width=30,
            command=self.apply_text,
        )
        self.apply.grid(row=0, column=1, padx=10, pady=10)

        self.btn = [
            [
                ctk.CTkButton(
                    self.frame_option,
                    font=self.fonts,
                    width=160,
                    fg_color="transparent",
                )
                for i in range(5)
            ]
            for j in range(4)
        ]

        self.btn[0][0] = self.make_btn(0, 0, "ID")
        self.btn[0][1] = self.make_btn(0, 1, "タイトル")
        self.btn[0][2] = self.make_btn(0, 2, "投稿者")
        self.btn[0][3] = self.make_btn(0, 3, "投稿者ID")
        self.btn[1][0] = self.make_btn(1, 0, "投稿日")
        self.btn[1][1] = self.make_btn(1, 1, "動画サイズ縦")
        self.btn[1][2] = self.make_btn(1, 2, "動画サイズ横")
        self.btn[1][3] = self.make_btn(1, 3, "FPS")
        self.btn[2][0] = self.make_btn(2, 0, "サイトドメイン")
        self.btn[2][1] = self.make_btn(2, 1, "プレイリスト名")
        self.btn[2][2] = self.make_btn(2, 2, "プレイリスト内番号")
        self.btn[2][3].configure(
            command=lambda: self.entry.delete(0, ctk.END), text="クリア"
        )
        self.btn[2][3].grid(row=2, column=3, padx=10, pady=10, sticky="nsew")

        for r in range(3):
            self.frame_option.rowconfigure(r, weight=1)
        for c in range(4):
            self.frame_option.columnconfigure(c, weight=1)

    def make_btn(self, r, c, text):
        self.btn[r][c].configure(
            command=lambda: self.entry.insert(ctk.END, '"' + text + '"'),
            text=text,
        )
        self.btn[r][c].grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

    def apply_text(self):
        text = self.entry.get()
        for key in self.dict.keys():
            text = text.replace('"' + key + '"', "%(" + self.dict[key] + ")s")
        app.ent_filename.delete(0, tk.END)
        app.ent_filename.insert(0, text)
        self.destroy()

    def load_text(self):
        text = app.ent_filename.get()
        for key in self.dict.keys():
            text = text.replace("%(" + self.dict[key] + ")s", '"' + key + '"')
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)


app = App()
app.protocol("WM_DELETE_WINDOW", app.write_config)
app.mainloop()
