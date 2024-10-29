import os

import requests
from bs4 import BeautifulSoup
from packaging import version


def get_release_note(url):
    # スクレイピングしたtxtの保存場所を指定
    log_file = "log.txt"

    # key→辞書型変換の際に必要な変数を定義
    Mode = 1
    value = ""
    dic = {}

    # logファイルが0バイト、またはアプデ前の状態だった場合はスクレイピングを行う
    this_version = "2.6.1"
    latest_log_version = "2.6.1"

    if os.stat(log_file).st_size == 0 or version.parse(this_version) < version.parse(
        latest_log_version
    ):
        # releasesのページ数を取得
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        page = soup.find_all(class_="pagination")
        for page in page:
            page_num = int(page.text[-6:-5])
            break

        # log.txtの中身を0バイトにして初期化
        with open(log_file, mode="w") as f:
            f.truncate(0)

        # releasesのバージョン・変更履歴をtxtで取得
        for i in range(page_num):
            url_page_num = url + "?page=" + str(i + 1)
            response = requests.get(url_page_num)
            soup = BeautifulSoup(response.text, "html.parser")
            note = soup.find_all(class_="Box-body")

            for note in note:
                # バージョンと変更履歴の要素を抽出
                versions = note.find_all(class_="Link--primary Link")
                changes = note.find_all(class_="markdown-body my-3")

                for ver in versions:
                    with open(log_file, mode="a", encoding="utf-8") as f:
                        f.write(ver.text + "\n")

                for change in changes:
                    with open(log_file, mode="a", encoding="utf-8") as f:
                        f.write(change.text + "\n")
                        f.write("\n")
                        f.write("---\n")

        # 大量に付随してくる余計なヌル文字を削除。ついでに「latest」表記も削除
        with open(log_file, "r+", encoding="UTF-8") as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            lines_to_delete = [5, 11]
            for i, line in enumerate(lines):
                if i not in lines_to_delete and line.strip():
                    f.write(line)

    # バージョン・変更履歴をtxtから辞書型に変換
    with open("log.txt", encoding="utf-8") as f:
        for line in f:
            if line == "---\n":
                dic[key] = value
                value = ""
                Mode = 1
            else:
                if Mode == 1:
                    key = line.strip()
                    Mode = 0
                else:
                    value += line

    return dic


if __name__ == "__main__":
    url = "https://github.com/okata-t/yt-dlp_GUI/releases"
    releases = get_release_note(url)
    print(releases)

    """
    #辞書型からの文字取り出しプログラム例
    keys = list(releases.keys())
    for i in range(len(releases)):
        key = keys[i]
        value = releases[key]
        print(keys[i] + "\n" + value)
    """
