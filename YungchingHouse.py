from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, csv
from datetime import datetime

# 設定 Selenium 瀏覽器
options = webdriver.ChromeOptions()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

rows = []

# 抓前兩頁
for n in range(1, 3):
    url = f'https://buy.yungching.com.tw/list/住宅_p/高雄市-_c/_rm?pg={n}'
    driver.get(url)
    time.sleep(5)  # 等待 JavaScript 載入

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('a', class_='link')  # 每個房屋卡片都是一個 <a class="link">

    for card in cards:
        row = []
        catch_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row.append(catch_time)

        # 房屋名稱
        name = card.find('div', class_='caseName')
        row.append(name.text.strip() if name else '無資料')

        # 地址
        addr = card.find('span', class_='address')
        row.append(addr.text.strip() if addr else '無資料')

        # 類型
        type_ = card.find('span', class_='caseType')
        row.append(type_.text.strip() if type_ else '無資料')

        # 建坪
        area = card.find('span', class_='regArea')
        row.append(area.text.strip() if area else '無資料')

        # 樓層
        floor = card.find('span', class_='floor')
        row.append(floor.text.strip() if floor else '無資料')

        # 格局
        room = card.find('span', class_='room')
        row.append(room.text.strip() if room else '無資料')

        # 備註
        note = card.find('span', class_='note')
        row.append(note.text.strip() if note else '無資料')

        # 房屋連結
        href = card['href']
        full_link = f'https://buy.yungching.com.tw/{href}'
        row.append(full_link)

        rows.append(row)

driver.quit()

# 存成 CSV
catch_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
with open(f'永慶房屋_高雄_{catch_time}.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['抓取時間', '名稱', '地址', '類型', '建坪', '樓層', '格局', '備註', '連結'])
    writer.writerows(rows)
