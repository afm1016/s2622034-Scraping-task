import time
import requests
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