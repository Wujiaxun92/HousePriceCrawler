#pip install urllib3==1.26.16

import requests #下載套件
from bs4 import BeautifulSoup #下載套件
import re
import time
import csv
from datetime import datetime

# 初始化儲存資料的列表
rows = []
# 爬取 1 到 n 頁
for n in range(1, 5):

    # 設定目標 URL，並將頁碼作為變數 `n` 插入
    url = f'https://www.sinyi.com.tw/buy/list/NewTaipei-city/default-desc/{n}'
    # 設定請求標頭，模擬瀏覽器請求
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

    # 發送 HTTP GET 請求並獲取 HTML 內容
    html = requests.get(url, headers=request_headers)
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html.text, 'html.parser')

    # 找到所有包含房屋物件的區塊
    tags = soup.find_all('div', class_='buy-list-item')

    # 針對每個房屋物件區塊進行資料提取
    for tag in tags:
        row = []

        # 抓取時間
        catch_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        row.append(catch_time)

        # 取得房屋的詳細頁面連結
        link = tag.find('a').get('href')
        row.append('https://www.sinyi.com.tw/' + link)

        # 抓取房屋標題
        title = tag.find('div', class_='LongInfoCard_Type_Name').text if tag.find('div',
                                                                                  class_='LongInfoCard_Type_Name') else '無資料'
        row.append(title)

        # 抓取房屋地址
        address_temp2 = tag.find('div', class_='LongInfoCard_Type_Address')
        address = address_temp2.find('span').text if address_temp2 and address_temp2.find('span') else '無資料'
        row.append(address)

        # 從地址欄位中提取屋齡資訊
        address_temp = address_temp2.text if address_temp2 else '無資料'
        house_old = re.findall(r'[0-9]+\.[0-9]+|預售|--', address_temp)
        row.append(house_old[0] if house_old else '無資料')

        # 提取物件類型（例如新成屋或預售屋）
        style = re.findall(r'年..|預售..|--..', address_temp)
        row.append(style[0] if style else '無資料')

        # 抓取坪數和樓層等房屋資訊
        size_temp = tag.find('div', class_='LongInfoCard_Type_HouseInfo').text if tag.find('div',
                                                                                           class_='LongInfoCard_Type_HouseInfo') else '無資料'
        size_temp2 = re.findall(r'[0-9]+\.[0-9]+|[0-9]+', size_temp)

        # 原始坪數
        original_size = size_temp2[0] if len(size_temp2) > 0 else '無資料'
        row.append(original_size)

        # 實際坪數
        real_size = size_temp2[1] if len(size_temp2) > 1 else '無資料'
        row.append(real_size)

        # 抓取房屋格局（例如幾房幾廳）
        layout = re.findall(r'.房....|.廳..', size_temp)
        row.append(layout[0] if layout else '無資料')

        # 提取樓層資訊
        total_floor = re.findall(r'[0-9]+', size_temp)[-1] if len(re.findall(r'[0-9]+', size_temp)) > 1 else '無資料'
        row.append(total_floor)

        # 實際樓層
        real_floor = re.findall(r'[0-9]+', size_temp)[-2] if len(re.findall(r'[0-9]+', size_temp)) > 1 else '無資料'
        row.append(real_floor)

        # 抓取物件的點擊次數
        info_temp = tag.find('div', class_='LongInfoCard_Type_SpecificTags').text if tag.find('div',
                                                                                              class_='LongInfoCard_Type_SpecificTags') else '無資料'
        clicks = re.findall(r'[0-9]+', info_temp)
        row.append(clicks[0] if clicks else '無資料')

        # 提取額外資訊（例如特定標籤）
        specific_info = tag.find_all('span', class_='specificTag')
        other_info_1 = specific_info[0].text if len(specific_info) > 0 else '無資料'
        row.append(other_info_1)

        other_info_2 = specific_info[1].text if len(specific_info) > 1 else '無資料'
        row.append(other_info_2)

        other_info_3 = specific_info[2].text if len(specific_info) > 2 else '無資料'
        row.append(other_info_3)

        # 抓取售價
        price_temp = tag.find('div', class_='LongInfoCard_Type_Right').text if tag.find('div',
                                                                                        class_='LongInfoCard_Type_Right') else '無資料'
        real_price = re.findall(r'[0-9]+\,[0-9]+|[0-9]+', price_temp)
        row.append(real_price[-1] if real_price else '無資料')

        # 將所有資料加入到 rows 列表
        rows.append(row)

    # 增加延遲時間以避免被網站屏蔽
    time.sleep(5)

# 以當前時間命名並儲存為 CSV 檔案
catch_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
with open(f'信義房屋_all_{catch_time}.csv', 'w', newline='', encoding='utf-8-sig') as file:
    data = csv.writer(file)
    data.writerow(
        ['抓取時間', '超連結', '物件標題', '地址', '屋齡', '物件類型', '原始坪數', '實際坪數', '格局', '總樓層',
         '所在樓層', '物件被點擊次數', '額外資訊1', '額外資訊2', '額外資訊3', '現在價格'])
    data.writerows(rows)
