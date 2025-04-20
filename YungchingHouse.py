import requests  # 下載套件
from bs4 import BeautifulSoup  # 下載套件
import time
import csv
from datetime import datetime

# 初始化儲存資料的列表
rows = []
# 爬取 1 到 n 頁
for n in range(1, 3):

    # 設定目標 URL，並將頁碼作為變數 `n` 插入
    url = f'https://buy.yungching.com.tw/region/%E4%BD%8F%E5%AE%85_p/%E5%8F%B0%E5%8C%97%E5%B8%82-_c/_rm/{n}'
    # 設定請求標頭，模擬瀏覽器請求
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

    # 發送 HTTP GET 請求並獲取 HTML 內容
    html = requests.get(url, headers=request_headers)
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html.text, 'html.parser')

    # 找到所有包含房屋物件的區塊
    tags = soup.find_all('div', class_='item-info')

    # 針對每個房屋物件區塊進行資料提取
    for tag in tags:
        row = []

        # 抓取時間
        catch_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        row.append(catch_time)

        # 尋找 class 為 item-info-detail 的 ul 標籤
        ul_tag = tag.find('ul', class_='item-info-detail')

        # 確保 ul_tag 存在
        if ul_tag:
            # 抓取 ul 中的所有 li 標籤
            li_tags = ul_tag.find_all('li')

            # 定義欄位列表，初始化為 '無資料'
            fields = ['物件類型', '屋齡', '樓層', '坪數1', '坪數2', '坪數3', '格局', '備註']
            li_contents = [li.text.strip() for li in li_tags]

            # 將 li 內容填入對應欄位（若不足則補 '無資料'）
            for i in range(len(fields)):
                row.append(li_contents[i] if i < len(li_contents) else '無資料')
        else:
            # 若 ul 不存在，則填入 '無資料'
            row.extend(['無資料'] * 8)

        # 將所有資料加入到 rows 列表
        rows.append(row)

    # 增加延遲時間以避免被網站屏蔽
    time.sleep(5)

# 以當前時間命名並儲存為 CSV 檔案
catch_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
with open(f'永慶房屋_li_{catch_time}.csv', 'w', newline='', encoding='utf-8-sig') as file:
    data = csv.writer(file)
    data.writerow(['抓取時間', '物件類型', '屋齡', '樓層', '坪數1', '坪數2', '坪數3', '格局', '備註'])
    data.writerows(rows)
