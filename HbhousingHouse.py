import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 初始化 WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(5)

# 目標網站 URL
url = "https://www.hbhousing.com.tw/BuyHouse/%E5%8F%B0%E5%8C%97%E5%B8%82/"
driver.get(url)

# 取得當前時間，並格式化為抓取時間，用於檔案命名
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"住商不動產_台北市_{current_time}.csv"

# 開啟 CSV 檔案以寫入資料
with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['抓取時間', '超連結', '物件標題', '資訊1', '資訊2'])  # 寫入表頭

    page_number = 1  # 用來追蹤當前頁碼

    while True:
        try:
            # 等待房屋資訊區塊加載完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "house__list__item"))
            )

            # 獲取所有房屋資訊
            houses = driver.find_elements(By.CLASS_NAME, "house__list__item")

            # 逐一處理每個房屋資訊
            for house in houses:
                try:
                    # 抓取時間
                    grab_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # 超連結
                    link_element = house.find_element(By.CLASS_NAME, "item__header__tit").find_element(
                        By.TAG_NAME, "a")
                    link = link_element.get_attribute("href").strip() if link_element else "無超連結"

                    # 物件標題
                    title = link_element.text.strip() if link_element else "無標題"

                    # 資訊1 和 資訊2
                    info_elements = house.find_elements(By.CLASS_NAME, "item__info__header")
                    info1 = info_elements[0].text.strip() if len(info_elements) > 0 else "無資訊1"

                    # 資訊2 是 <ul>，所以提取所有 <li> 的內容並合併
                    ul_element = house.find_element(By.CLASS_NAME, "item__info__table")
                    info2_list_items = ul_element.find_elements(By.TAG_NAME, "li")
                    info2 = " | ".join([item.text.strip() for item in info2_list_items]) if info2_list_items else "無資訊2"

                    # 寫入 CSV 檔案
                    writer.writerow([grab_time, link, title, info1, info2])
                    print(f"抓取成功:{title}")

                except Exception as e:
                    print(f"抓取單筆資料時發生錯誤: {e}")

            # 使用 XPath 定位並點擊翻頁按鈕
            try:
                # 使用 XPath 查找下一頁的按鈕
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//ul[contains(@class, 'house__list__pagenum')]//a[text()='>']"))
                )

                if "disabled" in next_button.get_attribute("class"):
                    print("已到最後一頁，停止抓取")
                    break

                # 點擊下一頁按鈕
                next_button.click()

                # 顯示翻頁訊息
                print("-" * 30)  # 加上分隔線
                print(f"翻到第 {page_number} 頁")

                # 等待新頁面加載
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(houses[0])
                )

                page_number += 1  # 更新頁碼

            except Exception as e:
                print(f"翻頁失敗: {e}")
                break

        except Exception as e:
            print(f"抓取頁面時發生錯誤: {e}")
            break

# 關閉瀏覽器
driver.quit()
print(f"抓取完成，資料已儲存至 {csv_filename}")