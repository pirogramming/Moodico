import os
import time
import json
import uuid
import requests
import numpy as np
from io import BytesIO
from PIL import Image
from skimage import color
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

TARGETS = [
    {"brand": "romand", "url": "https://romand.co.kr/product/maincatedetail.html?cate_code=289"},
    {"brand": "3ce", "url": "https://www.3cecosmetics.com/all-products/lips"}
]

SCROLL_COUNT = 4
SAVE_PATH = 'static/data/test_products.json'

# Selenium Chrome Driver 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

all_products = []

def extract_romand_items():
    items = driver.find_elements(By.CSS_SELECTOR, 'li.list_prd_item')
    results = []
    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, '.prd_title').text
            image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            price = item.find_element(By.CSS_SELECTOR, '.current_price').text.strip()
            url = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            results.append({
                "brand": "romand",
                "category": "Lips",
                "name": name,
                "color_name": name.split('/')[-1].strip(),
                "image": image,
                "price": price,
                "url": url
            })
        except Exception as e:
            print("Romand Error:", e)
            continue
    return results

def extract_3ce_items():
    items = driver.find_elements(By.CSS_SELECTOR, 'li.tce-grid__item')
    results = []
    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, 'h2.tce-product-card__name').text.strip()
            url = item.find_element(By.CSS_SELECTOR, 'a.tce-product-card__link').get_attribute("href")
            price = item.find_element(By.CSS_SELECTOR, '.tce-product-card__price').text.strip()
            image = item.find_element(By.CSS_SELECTOR, 'img.tce-product-card__image').get_attribute("src")

            results.append({
                "brand": "3CE",
                "category": "Lips",
                "name": name,
                "color_name": name.split('/')[-1].strip() if '/' in name else name,
                "url": f"https://www.3cecosmetics.com{url}" if url.startswith('/') else url,
                "image": f"https://www.3cecosmetics.com{image}" if image.startswith('/') else image,
                "price": price
            })
        except Exception as e:
            print("3CE Error:", e)
            continue
    return results

# 밝은 배경 제거
def extract_average_color(img_url):
    try:
        response = requests.get(img_url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        img = img.resize((50, 50))
        pixels = np.array(img).reshape(-1, 3)

        filtered = [px for px in pixels if not all(c > 240 for c in px)]
        if not filtered:
            filtered = pixels  

        avg_rgb = np.array(filtered).mean(axis=0)
        r, g, b = map(int, avg_rgb)
        hex_code = '#{:02x}{:02x}{:02x}'.format(r, g, b)

        rgb_norm = np.array([[avg_rgb]]) / 255.0
        lab = color.rgb2lab(rgb_norm)[0][0]
        lab_l, lab_a, lab_b = lab.round(2)

        return hex_code, lab_l, lab_a, lab_b
    except Exception as e:
        print(f"[Color Error] {img_url} - {e}")
        return "#000000", 0, 0, 0

# 스크랩핑 시작
for target in TARGETS:
    brand = target["brand"]
    url = target["url"]
    print(f"Scraping {brand}...")

    driver.get(url)
    time.sleep(2)

    for _ in range(SCROLL_COUNT):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    if brand == "romand":
        raw_items = extract_romand_items()
    elif brand == "3ce":
        raw_items = extract_3ce_items()
    else:
        print(f"No extractor defined for {brand}")
        continue

    print(f"  → {len(raw_items)} items found for {brand}")

    for item in raw_items:
        hex_color, lab_l, lab_a, lab_b = extract_average_color(item["image"])
        product = {
            "id": str(uuid.uuid4()),
            **item,
            "hex": hex_color,
            "lab_l": lab_l,
            "lab_a": lab_a,
            "lab_b": lab_b
        }
        all_products.append(product)

# 결과 저장
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
# with open(SAVE_PATH, 'w', encoding='utf-8') as f:
#     json.dump(all_products, f, ensure_ascii=False, indent=2)

driver.quit()
print(f"\nSaved {len(all_products)} products to {SAVE_PATH}")

test_products = all_products[:5] + all_products[-5:]
with open(SAVE_PATH,'w',encoding='utf-8') as f:
    json.dump(test_products,f,ensure_ascii=False,indent=2)
print("테스트용 JSON 생성 완료")