import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def safe_get_text(element, class_name, default="無資料"):
    """
    安全提取元素的文字
    """
    try:
        target = element.find_element(By.CLASS_NAME, class_name)
        return target.text.strip()
    except:
        return default


# 初始化 WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(5)

# 目標網站 URL
url = "https://buy.u-trust.com.tw/region/%E5%8F%B0%E5%8C%97%E5%B8%82_c"
driver.get(url)

# 取得當前時間，並格式化為抓取時間，用於檔案命名
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"有巢氏房屋_台北市_{current_time}.csv"

# 開啟 CSV 檔案以寫入資料
with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow([  # 寫入表頭
        '抓取時間', '超連結', '物件標題', '地址', '物件類型', '屋齡',
        '樓層', '土地坪數', '主要坪數', '建物坪數', '格局', '價格', '備註'
    ])

    while True:
        try:
            # 等待房屋資訊區塊加載完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "buy_list_item_info"))
            )

            # 獲取所有房屋資訊
            houses = driver.find_elements(By.CLASS_NAME, "buy_list_item_info")

            # 逐一處理每個房屋資訊
            for house in houses:
                try:
                    # 抓取時間
                    grab_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # 嘗試抓取超連結和物件標題
                    try:
                        link_element = house.find_element(By.CLASS_NAME, "item-caseName").find_element(By.TAG_NAME, "a")
                        link = link_element.get_attribute("href").strip() if link_element else "無超連結"
                        title = link_element.text.strip() if link_element else "無標題"
                    except Exception as e:
                        link = "無超連結"
                        title = "無標題"
                        print(f"無法取得超連結或標題: {e}")

                    # 地址
                    address = safe_get_text(house, "item-address")


                    # 找到 <ul> 裡的所有 <li>，並提取各項資料
                    info_list = house.find_elements(By.CSS_SELECTOR, "ul.item-tags > li")
                    obj_type = info_list[0].text.strip() if len(info_list) > 0 else "無物件類型"
                    age = info_list[1].text.strip() if len(info_list) > 1 else "無屋齡"
                    floor = info_list[2].text.strip() if len(info_list) > 2 else "無樓層"
                    land_area = info_list[3].text.strip() if len(info_list) > 3 else "無土地坪數"
                    main_area = info_list[4].text.strip() if len(info_list) > 4 else "無主要坪數"
                    building_area = info_list[5].text.strip() if len(info_list) > 5 else "無建物坪數"
                    layout = info_list[6].text.strip() if len(info_list) > 6 else "無格局"

                    # 價格
                    price = safe_get_text(house, "buy_list_item_price")

                    # 備註
                    try:
                        remark_element = house.find_element(By.CLASS_NAME, "item-description")
                        remark = remark_element.text.strip() if remark_element else "無備註"
                    except:
                        remark = "無備註"

                    # 寫入 CSV 檔案
                    writer.writerow([
                        grab_time, link, title, address, obj_type, age, floor,
                        land_area, main_area, building_area, layout, price, remark
                    ])
                    print(f"抓取成功: {title}")

                except Exception as e:
                    print(f"抓取單筆資料時發生錯誤: {e}")
                    continue  # 跳過此筆資料，繼續抓取下一筆

            # 找到下一頁按鈕並點擊
            try:
                next_button = driver.find_element(By.CLASS_NAME, "page_btn d-flex align-items-center")
                if "disabled" in next_button.get_attribute("class"):
                    print("已到最後一頁，停止抓取")
                    break
                next_button.click()

                # 等待新頁面加載
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(houses[0])
                )

            except Exception as e:
                print(f"翻頁失敗: {e}")
                break

        except Exception as e:
            print(f"抓取頁面時發生錯誤: {e}")
            break

# 關閉瀏覽器
driver.quit()
print(f"抓取完成，資料已儲存至 {csv_filename}")
