import customtkinter as ctk
from tkinter import messagebox


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
        ent_url = ctk.CTkEntry(self, width=400, placeholder_text="URL", font=self.fonts)
        ent_url.grid(row=0, column=0, padx=20, pady=20)
        btn_download = ctk.CTkButton(
            self, width=100, text="ダウンロード", command=self.download, font=self.fonts
        )
        btn_download.grid(row=0, column=1, padx=20, pady=20)

    def download(self):
        messagebox.showinfo("ダウンロード", "まだ作ってないよ")


app = App()
app.mainloop()
