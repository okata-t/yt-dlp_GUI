import configparser
import datetime
import gettext
import io
import math
import os
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
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
from PIL import Image
from pystray import Icon, Menu, MenuItem
from win11toast import toast

import color

VERSION = "v2.6.1"

config = configparser.ConfigParser(interpolation=None)
ini_path = "config.ini"

default_config = [
    ("Directory", "lastdir", os.path.join(os.path.expanduser("~"), "Downloads")),
    ("Directory", "filename", ""),
    ("Option", "language", "jp"),
    ("Option", "appearance", "System"),
    ("Option", "download_audio", "0"),
    ("Option", "embed_thumbnail", "0"),
    ("Option", "extension", "mp4"),
    ("Option", "browser", ""),
    ("Option", "resolution", "best"),
]


def read_config():
    if not os.path.exists(ini_path):
        fix_config()
    config.read(ini_path, encoding="utf-8")


def fix_config():
    for section, key, value in default_config:
        if not config.has_section(section):
            config[section] = {}
        if not config.has_option(section, key):
            config[section][key] = value
    with open(ini_path, "w") as f:
        config.write(f)
    read_config()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Windowsのテーマ色設定。"Light" or "Dark"
        self.color_mode = darkdetect.theme()

        ctk.set_appearance_mode("System")
        try:
            ctk.set_default_color_theme("theme.json")
        except FileNotFoundError:
            ctk.set_default_color_theme("blue")
        self.fonts = ("游ゴシック", 15)
        self.title("yt-dlp_GUI " + VERSION)
        self.iconbitmap("icon.ico")

        self.create_menu()
        self.setup()
        self.load_option()

        self.check_version(VERSION)
        self.check_option()
        self.select_appearance(self.appearance)
        self.set_submenu_color(self.languages, self.dict_language, self.language)
        self.set_submenu_color(self.appearances, self.dict_appearance, self.appearance)
        self.set_submenu_color(self.cookies, self.dict_browser, self.browser)

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
                title=_("アップデート"),
                message=_("新しいバージョン：")
                + latest_version
                + _("\nが公開されました。\nダウンロードしますか？"),
                icon="info",
                font=self.fonts,
                option_1=_("キャンセル"),
                option_2=_("ダウンロード"),
                option_3=_("GitHubへ"),
            )
            if msg.get() == _("GitHubへ"):
                webbrowser.open("https://github.com/okata-t/yt-dlp_GUI/releases/latest")
                sys.exit()
            elif msg.get() == _("ダウンロード"):
                webbrowser.open(
                    "https://github.com/okata-t/yt-dlp_GUI/releases/"
                    + "latest/download/yt-dlp_GUI_Setup.exe"
                )
                sys.exit()

    def uninstall(self):
        msg = CTkMessagebox.CTkMessagebox(
            title=_("アンインストール"),
            message=_("本当にアンインストールしますか？"),
            icon="info",
            font=self.fonts,
            option_1=_("キャンセル"),
            option_2=_("アンインストール"),
        )
        if msg.get() == _("アンインストール"):
            os.remove("config.ini")
            cp = subprocess.run("start unins000.exe", shell=True)
            if cp.returncode == 0:
                sys.exit()

    # メニューバーを追加
    def create_menu(self):
        self.color_selected = "#808080"
        if self.color_mode == "Dark":
            self.color_menubar = "#242424"
            self.color_edit = "#EBEBEB"
        else:
            self.color_menubar = "#EBEBEB"
            self.color_edit = "#242424"
        self.menu = CTkMenuBar.CTkMenuBar(self, bg_color=self.color_menubar)
        self.pack_propagate(0)

        menu_option = self.menu.add_cascade(_("設定"), font=self.fonts)
        menu_view = self.menu.add_cascade(_("表示"), font=self.fonts)
        menu_link = self.menu.add_cascade(_("リンクを開く"), font=self.fonts)
        menu_beta = self.menu.add_cascade(_("ベータ"), font=self.fonts)
        menu_others = self.menu.add_cascade(_("その他"), font=self.fonts)

        dropdown_option = CTkMenuBar.CustomDropdownMenu(menu_option, font=self.fonts)
        dropdown_view = CTkMenuBar.CustomDropdownMenu(menu_view, font=self.fonts)
        dropdown_link = CTkMenuBar.CustomDropdownMenu(menu_link, font=self.fonts)
        dropdown_beta = CTkMenuBar.CustomDropdownMenu(menu_beta, font=self.fonts)
        dropdown_others = CTkMenuBar.CustomDropdownMenu(menu_others, font=self.fonts)

        submenu_cookie = dropdown_option.add_submenu(_("Cookie設定"))
        self.cookies = []
        self.dict_browser = {
            _("なし"): "",
            "Brave": "brave",
            "Google Chrome": "chrome",
            "Microsoft Edge": "edge",
            "Mozilla FireFox": "firefox",
            "Opera": "opera",
            "Vivaldi": "vivaldi",
        }
        self.cookies.append(
            submenu_cookie.add_option(_("なし"), command=lambda: self.select_cookie(""))
        )
        self.cookies.append(
            submenu_cookie.add_option(
                "Brave", command=lambda: self.select_cookie("brave")
            )
        )
        self.cookies.append(
            submenu_cookie.add_option(
                "Google Chrome", command=lambda: self.select_cookie("chrome")
            )
        )
        self.cookies.append(
            submenu_cookie.add_option(
                "Microsoft Edge", command=lambda: self.select_cookie("edge")
            )
        )
        self.cookies.append(
            submenu_cookie.add_option(
                "Mozilla FireFox", command=lambda: self.select_cookie("firefox")
            )
        )
        self.cookies.append(
            submenu_cookie.add_option(
                "Opera", command=lambda: self.select_cookie("opera")
            )
        )
        self.cookies.append(
            submenu_cookie.add_option(
                "Vivaldi", command=lambda: self.select_cookie("vivaldi")
            )
        )

        self.submenu_language = dropdown_view.add_submenu(_("言語"))
        self.languages = []
        self.dict_language = {
            "日本語": "jp",
            "English": "en",
            "한국어": "kr",
        }
        self.languages.append(
            self.submenu_language.add_option(
                "日本語", command=lambda: self.select_language("jp")
            )
        )
        self.languages.append(
            self.submenu_language.add_option(
                "English", command=lambda: self.select_language("en")
            )
        )
        self.languages.append(
            self.submenu_language.add_option(
                "한국어", command=lambda: self.select_language("kr")
            )
        )

        self.submenu_appearance = dropdown_view.add_submenu(_("外観"))
        self.appearances = []
        self.dict_appearance = {
            _("システム(メニューバーは再起動時反映)"): "System",
            _("ダーク"): "Dark",
            _("ライト"): "Light",
        }
        self.appearances.append(
            self.submenu_appearance.add_option(
                _("システム(メニューバーは再起動時反映)"),
                command=lambda: self.select_appearance("System"),
            )
        )
        self.appearances.append(
            self.submenu_appearance.add_option(
                _("ダーク"), command=lambda: self.select_appearance("Dark")
            )
        )
        self.appearances.append(
            self.submenu_appearance.add_option(
                _("ライト"), command=lambda: self.select_appearance("Light")
            )
        )

        dropdown_view.add_option(
            _("テーマエディタを開く"),
            command=lambda: color.EditTheme(
                self, self.color_mode, "theme.json", self.fonts, self.language
            ),
        )

        dropdown_link.add_option(
            "GitHub",
            command=lambda: webbrowser.open("https://github.com/okata-t/yt-dlp_GUI"),
        )
        dropdown_link.add_option(
            "YouTube",
            command=lambda: webbrowser.open("https://www.youtube.com"),
        )
        dropdown_link.add_option(
            "ニコニコ動画",
            command=lambda: webbrowser.open("https://www.nicovideo.jp"),
        )
        dropdown_link.add_option(
            "Twitch",
            command=lambda: webbrowser.open("https://www.twitch.tv"),
        )

        dropdown_beta.add_option(_("クイックモード"), command=self.start_quick)

        dropdown_others.add_option(_("アンインストール"), command=self.uninstall)

    def restart(self, app):
        app.write_config(False)
        global _
        _ = gettext.translation(
            domain="messages",
            localedir="locale",
            languages=[self.language],
            fallback=True,
        ).gettext
        app = App()
        app.protocol("WM_DELETE_WINDOW", lambda: app.write_config(False))
        app.mainloop()

    def write_config(self, isQuick):
        with open(ini_path, "w", encoding="utf-8") as f:
            config["Directory"]["lastdir"] = self.ent_savedir.get()
            config["Directory"]["filename"] = self.ent_filename.get()
            config["Option"] = {}
            config["Option"]["language"] = self.language
            config["Option"]["appearance"] = self.appearance
            config["Option"]["download_audio"] = str(self.chk_audio.get())
            config["Option"]["embed_thumbnail"] = str(self.chk_thumbnail.get())
            config["Option"]["extension"] = str(self.cmb_extension.get())
            config["Option"]["browser"] = self.browser
            config["Option"]["resolution"] = (
                str(self.cmb_resoluion.get())
                if str(self.cmb_resoluion.get()) != _("最高画質")
                else "best"
            )
            config.write(f)
        if isQuick:
            self.withdraw()
        else:
            self.destroy()

    def load_option(self):
        try:
            self.language = config["Option"]["language"]
            self.appearance = config["Option"]["appearance"]
            self.var_chk_audio.set(config["Option"]["download_audio"])
            self.var_chk_thumbnail.set(config["Option"]["embed_thumbnail"])
            self.cmb_extension.set(config["Option"]["extension"])
            self.browser = config["Option"]["browser"]
            self.cmb_resoluion.set(
                config["Option"]["resolution"]
                if config["Option"]["resolution"] != "best"
                else _("最高画質")
            )
        except KeyError:
            fix_config()
            self.load_option()

    def check_option(self, *args):
        if self.var_chk_audio.get():
            self.cmb_extension.configure(values=self.dict_file["audio"])
            self.cmb_resoluion.configure(state="disabled")
            if self.cmb_extension.get() == "wav":
                self.var_chk_thumbnail.set(False)
                self.chk_thumbnail.configure(state="disabled")
            else:
                self.chk_thumbnail.configure(state="normal")
        else:
            self.cmb_extension.configure(values=self.dict_file["movie"])
            self.cmb_resoluion.configure(state="normal")
            if self.cmb_extension.get() == "webm":
                self.var_chk_thumbnail.set(False)
                self.chk_thumbnail.configure(state="disabled")
            else:
                self.chk_thumbnail.configure(state="normal")

        if self.var_chk_duration.get():
            self.ent_duration_start.configure(state="normal")
            self.lbl_duration_hyphen.configure(state="normal")
            self.ent_duration_end.configure(state="normal")
        else:

            self.ent_duration_start.configure(state="disabled")
            self.lbl_duration_hyphen.configure(state="disabled")
            self.ent_duration_end.configure(state="disabled")

    def change_extension(self, mode):
        if self.var_chk_audio.get():
            self.cmb_extension.set(self.dict_file["audio"][0])
        else:
            self.cmb_extension.set(self.dict_file["movie"][0])

    def select_cookie(self, browser):
        self.browser = browser
        self.set_submenu_color(self.cookies, self.dict_browser, self.browser)

    def select_language(self, language):
        self.language = language
        self.restart(self)

    def select_appearance(self, appearance):
        self.appearance = appearance if appearance != "" else "System"
        ctk.set_appearance_mode(self.appearance)
        if self.appearance == "Dark" or (
            self.appearance == "System" and self.color_mode == "Dark"
        ):
            self.color_menubar = "#242424"
            self.color_edit = "#EBEBEB"
        else:
            self.color_menubar = "#EBEBEB"
            self.color_edit = "#242424"
        self.menu.configure(bg_color=self.color_menubar)
        self.btn_editname.configure(text_color=self.color_edit)
        self.set_submenu_color(self.appearances, self.dict_appearance, self.appearance)

    def set_submenu_color(self, submenu, dict, option):
        for c in submenu:
            if c.cget("option") == [k for k, v in dict.items() if v == option][0]:
                c.configure(fg_color=self.color_selected)
            else:
                c.configure(fg_color="transparent")

    def setup(self):
        self.toplevel_window = None
        self.frame_main = ctk.CTkFrame(
            self,
        )
        self.frame_main.grid(row=0, column=0, padx=10, pady=(35, 10), sticky="nsew")

        self.frame_info = ctk.CTkFrame(self)
        self.frame_info.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_option = ctk.CTkFrame(self)
        self.frame_option.grid(
            row=0, column=1, rowspan=2, padx=10, pady=(35, 10), sticky="nsew"
        )

        self.frame_progress = ctk.CTkFrame(self)
        self.frame_progress.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.frame_main.columnconfigure(1, weight=1)
        self.frame_progress.columnconfigure(0, weight=1)

        self.ent_url = ctk.CTkEntry(
            self.frame_main, width=520, placeholder_text="URL", font=self.fonts
        )
        self.ent_url.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.btn_paste = ctk.CTkButton(
            self.frame_main,
            width=100,
            text=_("ペースト"),
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
            placeholder_text=_("保存先フォルダ"),
            font=self.fonts,
        )
        self.ent_savedir.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        if config["Directory"]["lastdir"] != "":
            self.ent_savedir.insert(0, config["Directory"]["lastdir"])

        self.btn_savedir = ctk.CTkButton(
            self.frame_main,
            width=100,
            text=_("参照"),
            command=self.savedir,
            font=self.fonts,
        )
        self.btn_savedir.grid(row=1, column=2, padx=10, pady=10)

        self.btn_editname = ctk.CTkButton(
            self.frame_main,
            width=10,
            text=_("編集"),
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
            placeholder_text=_("保存ファイル名(空白ならタイトル)"),
            font=self.fonts,
        )
        self.ent_filename.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        if config["Directory"]["filename"] != "":
            self.ent_filename.insert(0, config["Directory"]["filename"])

        self.btn_download = ctk.CTkButton(
            self.frame_main,
            width=100,
            text=_("ダウンロード"),
            command=self.start_download,
            font=self.fonts,
        )
        self.btn_download.grid(row=2, column=2, padx=10, pady=10)

        self.info = {}

        self.btn_info = ctk.CTkButton(
            self.frame_info,
            width=100,
            text=_("動画情報の取得"),
            font=self.fonts,
            command=self.start_get_info,
        )
        self.btn_info.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.lbl_info_title = ctk.CTkLabel(self.frame_info, font=self.fonts)
        self.lbl_info_img = ctk.CTkLabel(self.frame_info, text="")
        self.lbl_duration = ctk.CTkLabel(self.frame_info, font=self.fonts)
        self.var_chk_duration = ctk.BooleanVar()
        self.chk_duration = ctk.CTkCheckBox(
            self.frame_info,
            text=_("範囲指定でダウンロード"),
            font=self.fonts,
            variable=self.var_chk_duration,
            command=self.check_option,
        )
        self.ent_duration_start = ctk.CTkEntry(
            self.frame_info, font=self.fonts, width=60
        )
        self.lbl_duration_hyphen = ctk.CTkLabel(
            self.frame_info, text="-", font=self.fonts
        )
        self.ent_duration_end = ctk.CTkEntry(self.frame_info, font=self.fonts, width=60)

        self.lbl_progress = ctk.CTkLabel(
            self.frame_progress, text="\n", font=self.fonts
        )
        self.lbl_progress.grid(row=0, column=0, padx=10, sticky="w")

        self.lbl_eta = ctk.CTkLabel(self.frame_progress, text="\n", font=self.fonts)
        self.lbl_eta.grid(row=0, column=1, padx=10, sticky="e")

        self.pbar_progress = ctk.CTkProgressBar(self.frame_progress)
        self.pbar_progress.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        self.pbar_progress.set(0)

        self.var_chk_audio = ctk.BooleanVar()
        self.chk_audio = ctk.CTkCheckBox(
            self.frame_option,
            text=_("音声のみダウンロード"),
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
            text=_("サムネイルを埋め込む"),
            font=self.fonts,
            variable=self.var_chk_thumbnail,
        )
        self.chk_thumbnail.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.combobox_label1 = ctk.CTkLabel(
            self.frame_option, text=_("拡張子を選択"), font=self.fonts
        )
        self.combobox_label1.grid(row=2, column=0, padx=10, pady=(5, 0), sticky="ew")

        self.dict_file = {
            "movie": ["mp4", "webm"],
            "audio": ["mp3", "wav", "m4a", "opus"],
        }

        self.cmb_extension = ctk.CTkComboBox(
            self.frame_option,
            values=self.dict_file["movie"],
            font=self.fonts,
            command=self.check_option,
        )
        self.cmb_extension.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="ew")

        self.combobox_label2 = ctk.CTkLabel(
            self.frame_option, text=_("解像度を選択"), font=self.fonts
        )
        self.combobox_label2.grid(row=4, column=0, padx=10, pady=(5, 0), sticky="ew")

        self.resolution_size = [
            "144",
            "240",
            "360",
            "480",
            "720",
            "1080",
            "1440",
            "2160",
            "4320",
            _("最高画質"),
        ]

        self.cmb_resoluion = ctk.CTkComboBox(
            self.frame_option,
            values=self.resolution_size,
            font=self.fonts,
            command=self.check_option,
        )
        self.cmb_resoluion.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="ew")

    def paste(self):
        clip_text = pyperclip.paste()
        self.ent_url.delete(0, tk.END)
        self.ent_url.insert(0, clip_text)

    def savedir(self):
        inidir = config["Directory"]["lastdir"]
        file_path = filedialog.askdirectory(initialdir=inidir)
        self.ent_savedir.delete(0, tk.END)
        self.ent_savedir.insert(0, file_path)

    def start_get_info(self):
        self.thread_info = threading.Thread(target=self.get_info)
        self.thread_info.start()

    def get_info(self):
        opt = {}
        self.this_resolution = []
        url = self.ent_url.get()
        if self.browser != "":
            opt["cookiesfrombrowser"] = (self.browser,)
        with yt_dlp.YoutubeDL(opt) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                self.info = {
                    "title": info["title"],
                    "duration": info["duration"],
                    "tumbnail": info["thumbnail"],
                    "height": info["height"],
                }

                for i in range(len(self.resolution_size) - 1):
                    if int(info["height"]) >= int(self.resolution_size[i]):
                        self.this_resolution.append(self.resolution_size[i])
                self.this_resolution.append(_("最高画質"))
                print(self.this_resolution)
                self.cmb_resoluion.configure(values=self.this_resolution)

                self.lbl_info_title.configure(text=info["title"])
                self.lbl_info_title.grid(
                    row=0, column=1, columnspan=4, padx=10, pady=10, sticky="w"
                )
                self.frame_info.columnconfigure(1, weight=1)

                self.lbl_info_img.configure(
                    image=ctk.CTkImage(
                        dark_image=Image.open(
                            io.BytesIO(requests.get(info["thumbnail"]).content)
                        ),
                        size=(640, 360),
                    )
                )
                self.lbl_info_img.grid(
                    row=1, column=0, columnspan=5, padx=10, pady=10, sticky="w"
                )

                self.lbl_duration.configure(
                    text=str(
                        datetime.timedelta(seconds=round(float(self.info["duration"])))
                    )
                )
                self.lbl_duration.grid(row=2, column=0, padx=10, pady=10, sticky="w")

                self.chk_duration.grid(row=2, column=1, padx=10, pady=10)

                self.ent_duration_start.configure(placeholder_text="0:00:00")
                self.ent_duration_start.grid(row=2, column=2, padx=10, pady=10)

                self.lbl_duration_hyphen.grid(row=2, column=3, pady=10)

                self.ent_duration_end.configure(
                    placeholder_text=str(
                        datetime.timedelta(seconds=round(float(self.info["duration"])))
                    )
                )
                self.ent_duration_end.grid(row=2, column=4, padx=10, pady=10)

            except Exception as e:
                CTkMessagebox.CTkMessagebox(
                    title=_("エラーが発生しました"),
                    message=e,
                    icon="cancel",
                    font=self.fonts,
                )

    def start_download(self):
        resolution = self.cmb_resoluion.get()
        if resolution == _("最高画質"):
            format_text_mp4 = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        else:
            format_text_mp4 = (
                "bestvideo[ext=mp4][height<="
                + str(self.cmb_resoluion.get())
                + "]+bestaudio[ext=m4a]/best[ext=mp4]"
            )

        self.opt = {
            "progress_hooks": [self.progress_hook],
            "postprocessor_hooks": [self.postprocessor_hook],
            "postprocessors": [],
            "format": format_text_mp4,
        }
        file_path = self.ent_savedir.get()
        file_name = self.ent_filename.get()
        url = self.ent_url.get()

        if url == "":
            CTkMessagebox.CTkMessagebox(
                title=_("エラー"),
                message=_("URLを入力してください"),
                icon="cancel",
                font=self.fonts,
            )
            return
        if file_path == "":
            CTkMessagebox.CTkMessagebox(
                title=_("エラー"),
                message=_("保存フォルダを指定してください"),
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
            if resolution == _("最高画質"):
                format_text_mp4 = (
                    "bestvideo[ext=webm]/bestvideo+bestaudio/best[ext=mp4]"
                )
            else:
                format_text_webm = (
                    "best[ext=webm]/bestvideo[height<="
                    + str(self.cmb_resoluion.get())
                    + "]+bestaudio/best[ext=mp4]"
                )

            self.opt["format"] = format_text_webm
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

        def set_download_ranges(*args):
            duration_opt = [
                {
                    "start_time": datetime.timedelta(
                        hours=start_time.hour,
                        minutes=start_time.minute,
                        seconds=start_time.second,
                    ).total_seconds(),
                    "end_time": datetime.timedelta(
                        hours=end_time.hour,
                        minutes=end_time.minute,
                        seconds=end_time.second,
                    ).total_seconds(),
                }
            ]
            return duration_opt

        if self.chk_duration.get():
            start_time = datetime.datetime.strptime(self.ent_duration_start.get(), "%X")
            end_time = datetime.datetime.strptime(self.ent_duration_end.get(), "%X")
            self.opt["download_ranges"] = set_download_ranges

        if embed_thumbnail:
            self.opt["writethumbnail"] = True
            self.opt["postprocessors"].append({"key": "EmbedThumbnail"})

        if self.browser != "":
            self.opt["cookiesfrombrowser"] = (self.browser,)

        self.opt["outtmpl"] = file_path + "/" + file_name + ".%(ext)s"
        self.download_finished = 1 if download_audio else 2
        self.thread_download = threading.Thread(
            target=self.download, args=(url,), daemon=True
        )
        self.thread_download.start()

    def download(self, url):
        self.pbar_progress.set(0)
        self.lbl_progress.configure(text=_("\n準備中"))
        self.lbl_eta.configure(text="\n")
        with yt_dlp.YoutubeDL(self.opt) as ydl:
            try:
                ydl.download(url)
            except Exception as e:
                CTkMessagebox.CTkMessagebox(
                    title=_("エラーが発生しました"),
                    message=e,
                    icon="cancel",
                    font=self.fonts,
                )

    def progress_hook(self, d):
        self.filename = d.get("filename", "***")
        if d["status"] == "downloading":
            self.set_progress(
                self.download_finished,
                d.get("downloaded_bytes", None),
                d.get("total_bytes_estimate", None),
                d.get("speed", None),
                d.get("eta", None),
                self.filename,
            )

        elif d["status"] == "finished":
            self.download_finished -= 1

    def set_progress(
        self, downloading, downloaded_bytes, total_bytes, speed, eta, filename
    ):
        if downloading == 2:
            downloading_text = _("動画")
        else:
            downloading_text = _("音声")

        if total_bytes is None:
            total_bytes = downloaded_bytes

        self.lbl_progress.configure(
            text=(
                filename
                + "\n"
                + downloading_text
                + _("をダウンロード中：")
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
        self.lbl_eta.configure(text=_("\n残り ") + eta)
        self.pbar_progress.set(downloaded_bytes / total_bytes)

    def convert_size(self, size):
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
        i = math.floor(math.log(size, 1024)) if size > 0 else 0
        size = round(size / 1024**i, 2)
        return f"{size} {units[i]}"

    def postprocessor_hook(self, d):
        if d["status"] == "started":
            self.lbl_progress.configure(text=self.filename + _("\n処理中"))
            self.lbl_eta.configure(text="\n")

        elif d["status"] == "finished":
            if d["postprocessor"] == "MoveFiles":
                self.lbl_progress.configure(
                    text=self.filename + _("\nダウンロード完了")
                )
                self.lbl_eta.configure(text="\n")
                toast("yt-dlp_GUI", _("ダウンロードが完了しました"))

    def edit_filename(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = EditFilename(self)
        else:
            self.toplevel_window.focus()

    def start_quick(self):
        self.write_config(True)
        thread = threading.Thread(target=QuickMode)
        thread.start()


class EditFilename(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.fonts = ("游ゴシック", 15)
        self.title(_("ファイル名テンプレートの編集"))
        self.after(100, self.focus)

        self.dict = {
            "ID": "id",
            _("タイトル"): "title",
            "URL": "url",
            _("投稿者"): "uploader",
            _("投稿者ID"): "uploader_id",
            _("投稿日"): "upload_date",
            _("動画サイズ縦"): "width",
            _("動画サイズ横"): "height",
            "FPS": "fps",
            _("サイトドメイン"): "extractor",
            _("プレイリスト名"): "playlist",
            _("プレイリスト内番号"): "playlist_index",
        }

        self.frame_entry = ctk.CTkFrame(self)
        self.frame_entry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_option = ctk.CTkFrame(self)
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
            text=_("適用"),
            width=30,
            command=self.apply_text,
        )
        self.apply.grid(row=0, column=1, padx=10, pady=10)

        self.btn = [
            [
                ctk.CTkButton(
                    self.frame_option,
                    font=self.fonts,
                    fg_color="transparent",
                )
                for i in range(5)
            ]
            for j in range(4)
        ]

        self.btn[0][0] = self.make_btn(0, 0, "ID")
        self.btn[0][1] = self.make_btn(0, 1, _("タイトル"))
        self.btn[0][2] = self.make_btn(0, 2, _("投稿者"))
        self.btn[0][3] = self.make_btn(0, 3, _("投稿者ID"))
        self.btn[1][0] = self.make_btn(1, 0, _("投稿日"))
        self.btn[1][1] = self.make_btn(1, 1, _("動画サイズ縦"))
        self.btn[1][2] = self.make_btn(1, 2, _("動画サイズ横"))
        self.btn[1][3] = self.make_btn(1, 3, "FPS")
        self.btn[2][0] = self.make_btn(2, 0, _("サイトドメイン"))
        self.btn[2][1] = self.make_btn(2, 1, _("プレイリスト名"))
        self.btn[2][2] = self.make_btn(2, 2, _("プレイリスト内番号"))
        self.btn[2][3].configure(
            command=lambda: self.entry.delete(0, ctk.END), text=_("クリア")
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


class QuickMode:
    def __init__(self):
        image = Image.open("icon.ico")
        menu = Menu(
            MenuItem(_("ダウンロード"), self.download, default=True),
            MenuItem(_("クイックモードを終了する"), self.quit),
            MenuItem(_("yt-dlp_GUIを終了する"), lambda: os._exit(-1)),
        )
        self.icon = Icon(name="yt-dlp_GUI", icon=image, title="yt-dlp_GUI", menu=menu)
        self.icon.run()

    def quit(self):
        app.deiconify()
        self.icon.stop()

    def download(self):
        app.paste()
        app.start_download()


if __name__ == "__main__":
    read_config()
    try:
        language = config["Option"]["language"]
    except KeyError:
        fix_config()
        language = config["Option"]["language"]

    _ = gettext.translation(
        domain="messages",
        localedir="locale",
        languages=[language],
        fallback=True,
    ).gettext

    app = App()
    app.protocol("WM_DELETE_WINDOW", lambda: app.write_config(False))
    app.mainloop()
