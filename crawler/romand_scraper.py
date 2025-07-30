from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# 크롬 옵션
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# 크롬 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 크롤링할 URL
url = 'https://romand.co.kr/product/maincatedetail.html?cate_code=289'
driver.get(url)
time.sleep(3)

# 스크롤 다운 (3회)
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# 상품 요소 가져오기 (★ 셀렉터 변경됨!)
items = driver.find_elements(By.CSS_SELECTOR, 'li.list_prd_item')

print(f"총 {len(items)}개의 아이템을 찾았습니다.")

results = []
for item in items:
    try:
        name = item.find_element(By.CSS_SELECTOR, '.prd_title').text
        image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
        price = item.find_element(By.CSS_SELECTOR, '.current_price').text.strip()
        detail_url = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

        results.append({
            "name": name,
            "image": image,
            "price": price,
            "url": detail_url
        })

    except Exception as e:
        print("오류 발생:", e)
        continue

driver.quit()

# 저장
with open('static/data/romand_products.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
