import time
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

url = 'https://www.musashino-u.ac.jp/'

# アクセス前に1秒待つ
time.sleep(1)
res = requests.get(url, timeout=30)

print(f"ステータスコード：{res.status_code}")
res.raise_for_status()

# 取得したHTMLからタイトルを取り出す
html_soup = BeautifulSoup(res.content, 'html.parser')
title = html_soup.title.string
print(f"タイトル：{title}")

# URLをキー、タイトルを値として辞書に保存する
pages = {}
pages[url] = title
print(pages)

# トップページと同じドメインを判定するために取得する
domain = urlparse(url).netloc

# href属性があるaタグをすべて取得する
links = html_soup.find_all('a', href=True)
same_domain_urls = []

for link in links:
    # 相対URLを完全なURLに変換する
    next_url = urljoin(res.url, link['href'])

    # 「#」以降のページ内の移動先を取り除く
    next_url = urldefrag(next_url)[0]

    # URLを分解する
    parsed_url = urlparse(next_url)

    # 同一ドメインのHTTP・HTTPSリンクだけを残す
    if parsed_url.scheme in ('http', 'https') and parsed_url.netloc == domain:
        if next_url not in same_domain_urls:
            same_domain_urls.append(next_url)

for next_url in same_domain_urls:
    print(next_url)

print(f"同一ドメインの重複しないURL数：{len(same_domain_urls)}")

# リンク一覧に追加されたURLを順番に処理する
index = 0
while index < len(same_domain_urls):
    page_url = same_domain_urls[index]
    index += 1
    # すでにタイトルを保存したページは飛ばす
    if page_url in pages:
        continue

    time.sleep(1)
    try:
        res = requests.get(page_url, timeout=30)
        res.raise_for_status()
    except requests.RequestException as error:
        print(f"取得失敗：{page_url}：{error}")
        continue

    # 別ドメインへ転送された場合は解析しない
    if urlparse(res.url).netloc != domain:
        continue

    # HTML以外のファイルは解析しない
    content_type = res.headers.get('Content-Type', '').lower()
    if 'text/html' not in content_type:
        continue

    html_soup = BeautifulSoup(res.content, 'html.parser')

    # titleタグがある場合は文字列を取得する
    if html_soup.title is not None:
        title = html_soup.title.get_text()
    else:
        title = ''

    pages[page_url] = title
    print(f"{page_url} → {title}")
    links = html_soup.find_all('a', href=True)

    for link in links:
        next_url = urljoin(res.url, link['href'])
        next_url = urldefrag(next_url)[0]
        parsed_url = urlparse(next_url)

        if parsed_url.scheme in ('http', 'https') and parsed_url.netloc == domain:
            if next_url not in same_domain_urls:
                same_domain_urls.append(next_url)

print(f"タイトルを保存したページ数：{len(pages)}")
print(f"リンク先も調べた後のURL数：{len(same_domain_urls)}")

# 辞書に保存したURLとタイトルをCSVファイルに保存する
with open('sitemap.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['URL', 'タイトル'])
    writer.writerows(pages.items())

print('sitemap.csvに保存しました')