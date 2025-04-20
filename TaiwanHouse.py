import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 初始化 WebDriver，使用 WebDriver Manager 自動下載和管理 ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 開啟目標網站
url = ("https://www.twhg.com.tw/object_list-A.php?city=%E5%8F%B0%E5%8C%97%E5%B8%82&kid=9")
driver.get(url)

# 設定隱式等待時間（單位：秒），以確保元素在操作之前加載完成
driver.implicitly_wait(10)

# 取得當前時間，並格式化為抓取時間，用於檔案命名
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"台灣房屋_台北市_{current_time}.csv"

# 開啟 CSV 檔案以寫入房屋資訊
with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['抓取時間', '超連結', '物件標題', '地址', '坪數', '格局', '價格'])  # 寫入表頭

    # 記錄已抓取過的頁面，避免重複抓取
    processed_pages = set()

    while True:  # 不停翻頁直到找不到下一頁
        try:
            # 獲取當前頁的頁碼
            active_page_element = driver.find_element(By.CSS_SELECTOR, "a.active")
            active_page_number = int(active_page_element.text.strip())
            print(f"當前頁數: {active_page_number}")

            if active_page_number in processed_pages:
                print("此頁已抓取過，跳過")
                break  # 如果已經抓取過這一頁則退出

            # 加入處理過的頁面
            processed_pages.add(active_page_number)
        except Exception as e:
            print(f"無法獲取當前頁數: {e}")
            break  # 若無法獲取當前頁數，跳出循環

        # 等待房屋資料區塊加載完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "object_list-A-list-li"))
        )

        houses = driver.find_elements(By.CLASS_NAME, "object_list-A-list-li")  # 房屋資訊區塊

        # 抓取每一頁的房屋資訊
        for house in houses:
            try:
                # 抓取時間
                grab_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 超連結
                link_element = house.find_element(By.CLASS_NAME, "object_list-A-list-name").find_element(By.TAG_NAME,"a")
                link = link_element.get_attribute("href").strip() if link_element else "無超連結"

                # 物件標題
                title = link_element.text.strip() if link_element else "無標題"

                # 地址
                address_element = house.find_element(By.CLASS_NAME, "object_list-A-list-address")
                address = address_element.text.strip() if address_element else "無地址"

                # 房屋資訊：坪數和格局
                pattern_elements = house.find_elements(By.CLASS_NAME, "object_list-A-list-pattern")
                size = pattern_elements[0].text.strip() if len(pattern_elements) > 0 else "無坪數"
                layout = pattern_elements[1].text.strip() if len(pattern_elements) > 1 else "無格局"

                # 價格
                price_element = house.find_element(By.CLASS_NAME, "object_list-A-list-price")
                price = price_element.text.strip() if price_element else "無價格"

                # 寫入 CSV 檔案
                writer.writerow([grab_time, link, title, address, size, layout, price])
                print(
                    f"抓取時間: {grab_time}\n超連結: {link}\n標題: {title}\n地址: {address}\n坪數: {size}\n格局: {layout}\n價格: {price}\n{'-' * 30}")

            except Exception as e:
                # 若有任何抓取錯誤，標註為無法抓取的資料
                print(f"抓取錯誤: {e}")
                writer.writerow(
                    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "無超連結", "無標題", "無地址", "無坪數", "無格局",
                     "無價格"])

        try:
            # 獲取所有頁碼按鈕
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "div.paginate a")

            # 確保頁碼按鈕是可點擊的，並點擊下一頁
            for button in page_buttons:
                page_number = button.text.strip()
                if page_number.isdigit():
                    page_number = int(page_number)
                    if page_number == active_page_number + 1:
                        print(f"點擊第 {page_number} 頁")
                        button.click()  # 點擊該頁碼按鈕
                        break  # 點擊後跳出循環
            else:
                print("已經是最後一頁，停止抓取")
                break  # 如果沒有更多頁面，停止抓取

            # 等待新頁面加載
            WebDriverWait(driver, 10).until(
                EC.staleness_of(houses[0])  # 等待頁面內容更新
            )

        except Exception as e:
            print(f"無法翻頁: {e}，停止抓取")
            break  # 如果翻頁錯誤或已經是最後一頁，停止抓取

# 關閉瀏覽器，釋放資源
driver.quit()
print(f"抓取完成，資料已儲存至 {csv_filename}")
