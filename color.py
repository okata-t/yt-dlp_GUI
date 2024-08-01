import colorsys
import configparser
import json
import tkinter as tk

import customtkinter as ctk
import matplotlib.colors as mcolors


class App(ctk.CTk):
    config = configparser.ConfigParser()

    def __init__(self, appearance, theme, font):
        super().__init__()
        self.title("テーマエディター")
        self.geometry("600x420")
        ctk.set_appearance_mode(appearance)
        try:
            ctk.set_default_color_theme(theme)
        except FileNotFoundError:
            ctk.set_default_color_theme("blue")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.font = font
        self.config.read("color.ini", encoding="shift-jis")
        # color list
        try:
            self.current_color = (
                self.config["Colors"]["color"]
                .translate(str.maketrans("", "", " [']"))
                .split(",")
            )
        except KeyError:
            self.current_color = [
                "#27577D",
                "#36719F",
                "#3B8ED0",
                "#203A4F",
                "#144870",
                "#1F6AA5",
            ]
        self.color_bar_list = [
            f"{mcolors.to_hex(colorsys.hsv_to_rgb(hue/72, 0.7, 0.65))}"
            for hue in range(72)
        ]

        # create frame
        self.frame = [ctk.CTkFrame(self, corner_radius=10) for _ in range(3)]
        self.frame[0].grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.frame[1].grid(
            row=1, column=0, padx=20, pady=(0, 10), ipadx=10, ipady=10, sticky="nsew"
        )
        self.frame[2].grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.frame[0].grid_columnconfigure(1, weight=1)
        self.frame[1].grid_rowconfigure((1, 2, 3), weight=1)
        self.frame[1].grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.frame[2].grid_columnconfigure(0, weight=1)

        # frame[0] - Color bar
        self.color_bar_frame = ctk.CTkFrame(
            self.frame[0], corner_radius=0, height=30, fg_color="transparent"
        )
        self.color_bar_frame.grid(row=0, column=1, padx=(6, 16), pady=10, sticky="nsew")
        self.color_bar_frame.grid_rowconfigure(0, weight=1)
        self.color_bar_frame.grid_columnconfigure(
            tuple(range(len(self.color_bar_list))), weight=1
        )
        self.color_bar = [
            ctk.CTkLabel(
                self.color_bar_frame,
                corner_radius=0,
                fg_color=f"{color}",
                text="",
                padx=0,
                pady=0,
            )
            for color in self.color_bar_list
        ]
        for i in range(72):
            self.color_bar[i].grid(row=0, column=i, padx=0, pady=0, sticky="nsew")

        # frame[0] - Slider for selecting color
        self.label_hsv = [
            ctk.CTkLabel(self.frame[0], text=f"{item}")
            for item in ["色相", "彩度", "明度"]
        ]
        self.slider_hsv = [
            ctk.CTkSlider(
                self.frame[0],
                from_=0,
                to=1,
                number_of_steps=i,
                orientation="horizontal",
                command=self.color_set,
            )
            for i in [72, 11, 11]
        ]
        self.init_slider(self.current_color)
        for i in range(3):
            self.label_hsv[i].grid(
                row=i + 1,
                column=0,
                padx=(10, 0),
                pady=(0 if i < 2 else (0, 10)),
                sticky="nsew",
            )
            self.slider_hsv[i].grid(
                row=i + 1,
                column=1,
                padx=(0, 10),
                pady=(0 if i < 2 else (0, 10)),
                sticky="ew",
            )

        # frame[1] - color sample
        self.label_color1 = ctk.CTkLabel(
            self.frame[1],
            anchor="center",
            corner_radius=6,
            text="現在のテーマ",
            fg_color=self.current_color[0],
        )
        self.label_color1.grid(
            row=0, column=0, columnspan=2, padx=(10, 3), pady=(10, 3), sticky="ew"
        )
        self.label_color2 = ctk.CTkLabel(
            self.frame[1],
            corner_radius=6,
            fg_color=self.current_color[0],
            text="新規テーマ",
        )
        self.label_color2.grid(
            row=0, column=2, columnspan=2, padx=(3, 10), pady=(10, 3), sticky="ew"
        )
        self.color_label = [
            ctk.CTkEntry(
                self.frame[1],
                corner_radius=6,
                border_width=0,
                fg_color=f"{color}",
                justify="center",
            )
            for color in self.current_color * 2
        ]
        for i, color in enumerate(self.current_color * 2):
            self.color_label[i].grid(
                row=i % 3 + 1,
                column=i // 3,
                padx=((10, 3) if i // 3 == 0 else (3, 10) if i // 3 == 3 else 3),
                pady=((3, 10) if i % 3 == 3 else 3),
                sticky="nsew",
            )
            self.color_label[i].insert(0, f"{color}")

        self.save_button = ctk.CTkButton(
            self.frame[2],
            text="テーマを適用",
            font=self.font,
            command=self.save_json,
        )
        self.save_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # 参考用カラーの表示設定
    def reference_color(self):
        # OptionMenuから選択した情報を元にcolorに配色リストを代入
        color = self.current_color
        # 参考用カラーの適用
        self.label_color1.configure(
            fg_color=color[5], button_color=color[4], button_hover_color=color[3]
        )
        self.save_button.configure(fg_color=color[5])
        for i in range(len(color)):
            self.color_label[i].configure(fg_color=color[i])
            self.color_label[i].delete(0, tk.END)
            self.color_label[i].insert(0, color[i])

    def init_slider(self, current_color):
        self.bases = [
            [0.53, 0.4],
            [0.5, 0.5],
            [0.55, 0.7],
            [0.45, 0.25],
            [0.65, 0.33],
            [0.66, 0.49],
        ]
        hue, sat, val = colorsys.rgb_to_hsv(
            mcolors.to_rgb(current_color[0])[0],
            mcolors.to_rgb(current_color[0])[1],
            mcolors.to_rgb(current_color[0])[2],
        )

        self.slider_hsv[0].set(hue)
        self.slider_hsv[1].set((sat + 0.45 - self.bases[0][0]) / 0.55)
        self.slider_hsv[2].set((val + 0.25 - self.bases[0][1]) / 0.55)

    # カスタムテーマとなる配色の表示設定
    def color_set(self, event):
        # スライダーからHSVの数値を取得（0～1）
        hue, sat, val = (
            self.slider_hsv[0].get(),
            self.slider_hsv[1].get(),
            self.slider_hsv[2].get(),
        )

        # スライダーから取得したHSV値と初期値から16進数表記のカラーコードを生成
        self.colors = [
            f"{mcolors.to_hex(colorsys.hsv_to_rgb(hue, base[0]-0.45+sat*0.55, base[1]-0.25+val*0.55))}"
            for i, base in enumerate(self.bases)
        ]
        # ウィジェットへ適用
        for i in range(len(self.bases), len(self.bases) * 2):
            self.color_label[i].configure(fg_color=self.colors[i - len(self.bases)])
            self.label_color2.configure(fg_color=self.colors[0])
            self.color_label[i].delete(0, tk.END)
            self.color_label[i].insert(0, self.colors[i - len(self.bases)])

    def save_json(self):
        default_json = """{
            "CTk": {
                "fg_color": ["gray95", "gray10"]
            },
            "CTkToplevel": {
                "fg_color": ["gray95", "gray10"]
            },
            "CTkFrame": {
                "corner_radius": 6,
                "border_width": 0,
                "fg_color": ["gray90", "gray13"],
                "top_fg_color": ["gray85", "gray16"],
                "border_color": ["gray65", "gray28"]
            },
            "CTkButton": {
                "corner_radius": 6,
                "border_width": 0,
                "fg_color": ["#3a7ebf", "#1f538d"],
                "hover_color": ["#325882", "#14375e"],
                "border_color": ["grey27", "grey60"],
                "text_color": ["grey89", "grey89"],
                "text_color_disabled": ["gray74", "gray60"]
            },
            "CTkLabel": {
                "corner_radius": 0,
                "fg_color": "transparent",
                "text_color": ["gray14", "gray84"]
            },
            "CTkEntry": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": ["gray98", "gray21"],
                "border_color": ["gray61", "grey35"],
                "text_color": ["gray14", "gray84"],
                "placeholder_text_color": ["gray52", "gray62"]
            },
            "CTkCheckbox": {
                "corner_radius": 6,
                "border_width": 3,
                "fg_color": ["#3a7ebf", "#1f538d"],
                "border_color": ["grey27", "grey60"],
                "hover_color": ["#325882", "#14375e"],
                "checkmark_color": ["grey89", "gray90"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray60", "gray45"]
            },
            "CTkSwitch": {
                "corner_radius": 1000,
                "border_width": 3,
                "button_length": 0,
                "fg_Color": ["gray60", "grey30"],
                "progress_color": ["#3a7ebf", "#1f538d"],
                "button_color": ["gray36", "gray85"],
                "button_hover_color": ["gray20", "gray100"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray60", "gray45"]
            },
            "CTkRadiobutton": {
                "corner_radius": 1000,
                "border_width_checked": 6,
                "border_width_unchecked": 3,
                "fg_color": ["#3a7ebf", "#1f538d"],
                "border_color": ["grey27", "grey60"],
                "hover_color": ["#325882", "#14375e"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray60", "gray45"]
            },
            "CTkProgressBar": {
                "corner_radius": 1000,
                "border_width": 0,
                "fg_color": ["gray60", "grey30"],
                "progress_color": ["#3a7ebf", "#1f538d"],
                "border_color": ["gray", "gray"]
            },
            "CTkSlider": {
                "corner_radius": 1000,
                "button_corner_radius": 1000,
                "border_width": 6,
                "button_length": 0,
                "fg_color": ["gray60", "grey30"],
                "progress_color": ["gray40", "gray69"],
                "button_color": ["#3a7ebf", "#1f538d"],
                "button_hover_color": ["#325882", "#14375e"]
            },
            "CTkOptionMenu": {
                "corner_radius": 6,
                "fg_color": ["#3a7ebf", "#1f538d"],
                "button_color": ["#325882", "#14375e"],
                "button_hover_color": ["#234567", "#1e2c40"],
                "text_color": ["grey89", "grey89"],
                "text_color_disabled": ["gray74", "gray60"]
            },
            "CTkComboBox": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": ["gray98", "gray21"],
                "border_color": ["gray61", "grey35"],
                "button_color": ["gray61", "grey35"],
                "button_hover_color": ["grey44", "grey52"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray50", "gray45"]
            },
            "CTkScrollbar": {
                "corner_radius": 1000,
                "border_spacing": 4,
                "fg_color": "transparent",
                "button_color": ["gray55", "gray41"],
                "button_hover_color": ["gray40", "gray53"]
            },
            "CTkSegmentedButton": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": ["gray61", "gray29"],
                "selected_color": ["#3a7ebf", "#1f538d"],
                "selected_hover_color": ["#325882", "#14375e"],
                "unselected_color": ["gray61", "gray29"],
                "unselected_hover_color": ["gray70", "gray41"],
                "text_color": ["grey89", "grey89"],
                "text_color_disabled": ["gray74", "gray60"]
            },
            "CTkTextbox": {
                "corner_radius": 6,
                "border_width": 0,
                "fg_color": ["gray100", "gray20"],
                "border_color": ["gray61", "grey35"],
                "text_color": ["gray14", "gray84"],
                "scrollbar_button_color": ["gray55", "gray41"],
                "scrollbar_button_hover_color": ["gray40", "gray53"]
            },
            "CTkScrollableFrame": {
                "label_fg_color": ["gray80", "gray21"]
            },
            "DropdownMenu": {
                "fg_color": ["gray90", "gray20"],
                "hover_color": ["gray75", "gray28"],
                "text_color": ["gray14", "gray84"]
            },
            "CTkFont": {
                "macOS": {
                    "family": "SF Display",
                    "size": 13,
                    "weight": "normal"
                },
                "Windows": {
                    "family": "Roboto",
                    "size": 13,
                    "weight": "normal"
                },
                "Linux": {
                    "family": "Roboto",
                    "size": 13,
                    "weight": "normal"
                }
            }
        }
        """

        # 置換元の色のリスト
        replace_words = [
            "#234567",
            "#325882",
            "#3a7ebf",
            "#1e2c40",
            "#14375e",
            "#1f538d",
        ]
        # エントリーボックスから置換先のリストを取得
        colors = [
            self.color_label[i + len(replace_words)].get()
            for i in range(len(replace_words))
        ]
        # 色を置換
        for i, replace_word in enumerate(replace_words):
            default_json = default_json.replace(replace_word, colors[i])
        default_json = json.loads(default_json)
        self.config["Colors"] = {}
        self.config["Colors"]["color"] = str(colors)
        with open("color.ini", "w") as f:
            self.config.write(f)
        with open("theme.json", "w") as f:
            json.dump(default_json, f, indent=4)
        self.quit()
        self.destroy()


def main(appearance, theme, font):
    app = App(appearance, theme, font)
    app.protocol("WM_DELETE_WINDOW", lambda: [app.quit(), app.destroy()])
    app.mainloop()


if __name__ == "__main__":
    main("System", "blue", ("游ゴシック", 15))
