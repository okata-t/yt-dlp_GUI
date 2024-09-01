import requests
from bs4 import BeautifulSoup

def get_release_note(url):
    # releasesのページ数を取得
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    page = soup.find_all(class_="pagination")
    for page in page:
        page_num = int(page.text[-6:-5])
        break

    # バージョンと変更履歴を直接辞書型に変換
    releases = {}
    for i in range(page_num):
        url_page_num = url + "?page=" + str(i+1)
        response = requests.get(url_page_num)
        soup = BeautifulSoup(response.text, "html.parser")
        note = soup.find_all(class_="Box-body")

        for note in note:
            # バージョンと変更履歴の要素を抽出
            versions = note.find_all(class_="Link--primary Link")
            changes = note.find_all(class_="markdown-body my-3")

            # 最初のバージョンのみ取得し、変更履歴を結合
            version = versions[0].text.strip()
            changes = "\n".join([change.text.strip() for change in changes])
            changes = changes.replace("\n\n", "\n")
            releases[version] = changes

    return releases

if __name__ == "__main__":
    url = "https://github.com/okata-t/yt-dlp_GUI/releases"
    result = get_release_note(url)

    keys = list(result.keys())
    for i in range(len(result)):
        key = keys[i]
        value = result[key]
        print(keys[i] + "\n" + value)