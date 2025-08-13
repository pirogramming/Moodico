# TODO
# python manage.py scraper
import os
import time
import json
import uuid
import requests
import numpy as np
from io import BytesIO
from PIL import Image
from skimage import color
from skimage.color import rgb2lab  # used in get_product_color_w_kmeans
from collections import Counter     # used in get_product_color_w_kmeans
import cv2                          # used in get_product_color_w_kmeans
from sklearn.cluster import KMeans  # used in get_product_color_w_kmeans

from django.core.management.base import BaseCommand
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


TARGETS = [
    {"brand": "romand", "url": "https://romand.co.kr/product/maincatedetail.html?cate_code=289", "category": "Lips"},
    {"brand": "3ce", "url": "https://www.3cecosmetics.com/all-products/lips", "category": "Lips"},
    {"brand": "3ce", "url": "https://www.3cecosmetics.com/all-products/cheeks/blush", "category": "blush"},
    {"brand": "3ce", "url": "https://www.3cecosmetics.com/all-products/eyes/eyeshadow", "category": "eyeshadow"}
]

SCROLL_COUNT = 4
SAVE_PATH = os.path.join(settings.MEDIA_ROOT, 'data', 'all_products.json')
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

def extract_romand_items(driver, category):
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
                "category": category,
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

def extract_3ce_items(driver, category):
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
                "category": category,
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

def get_product_color_w_kmeans(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        pil_img = Image.open(BytesIO(response.content)).convert("RGB")
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        mask = np.zeros(cv_img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        height, width = cv_img.shape[:2]
        roi_rect = (int(width * 0.1), int(height * 0.1), int(width * 0.8), int(height * 0.8))

        cv2.grabCut(cv_img, mask, roi_rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        final_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        img_fg_only = cv_img * final_mask[:, :, np.newaxis]

        pixels = cv2.cvtColor(img_fg_only, cv2.COLOR_BGR2RGB).reshape(-1, 3)
        foreground_pixels = pixels[pixels.any(axis=1)]

        k = 4
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(foreground_pixels)

        rgb_colors = kmeans.cluster_centers_.astype('uint8')
        labels = kmeans.labels_
        hsv_colors = cv2.cvtColor(rgb_colors.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV)

        pixel_counts = Counter(labels)
        clusters = []
        for i in range(len(rgb_colors)):
            clusters.append({
                'index': i,
                'rgb': rgb_colors[i],
                'hsv': hsv_colors[i][0],
                'count': pixel_counts.get(i, 0)
            })
        clusters_sorted_by_value = sorted(clusters, key=lambda x: x['hsv'][2])
        candidate_clusters = clusters_sorted_by_value[1:-1] if len(clusters_sorted_by_value) > 2 else clusters_sorted_by_value
        final_cluster = max(candidate_clusters, key=lambda x: x['hsv'][1])

        best_color_rgb = final_cluster['rgb']
        final_hex_code = f"#{int(best_color_rgb[0]):02x}{int(best_color_rgb[1]):02x}{int(best_color_rgb[2]):02x}"
        lab_values = rgb2lab(np.uint8(best_color_rgb).reshape(1, 1, 3) / 255.0).flatten()
        print(f"{lab_values}, {final_hex_code}")

        return final_hex_code, lab_values

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {image_url}, 오류: {e}")
        return None, None
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return None, None

class Command(BaseCommand):
    help = "Scrape products and save JSON under MEDIA_ROOT/data/all_products.json"

    def handle(self, *args, **options):
        # Selenium Chrome Driver 설정
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        all_products = []

        # 스크랩핑 시작
        for target in TARGETS:
            brand = target["brand"]
            url = target["url"]
            category = target["category"]
            print(f"Scraping {brand}...")

            driver.get(url)
            time.sleep(2)

            for _ in range(SCROLL_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            if brand == "romand":
                raw_items = extract_romand_items(driver, category)
            elif brand == "3ce":
                raw_items = extract_3ce_items(driver, category)
            else:
                print(f"No extractor defined for {brand}")
                continue

            print(f"  → {len(raw_items)} items found for {brand} ({category})")

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

        # (원본 스크립트 로직 유지) — KMeans 재추출 루프
        new_data = []
        process_num = 0
        for product in all_products:
            process_num += 1
            image_url = product.get("image")
            print(f"{process_num}. {product['name']} 처리 중 ..")
            new_hex, new_lab = get_product_color_w_kmeans(image_url)

            new_product_object = product.copy()
            if new_lab is not None:
                new_product_object['hex'] = new_hex
                new_product_object['lab_l'] = round(new_lab[0], 2)
                new_product_object['lab_a'] = round(new_lab[1], 2)
                new_product_object['lab_b'] = round(new_lab[2], 2)
            new_data.append(new_product_object)

        # 결과 저장 (원본과 동일하게 all_products를 저장)
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)

        driver.quit()
        print(f"\nSaved {len(all_products)} products to {SAVE_PATH}")

        # 테스트 저장 주석 로직 유지
        # test_products = all_products[:5] + all_products[-5:]
        # with open(SAVE_PATH,'w',encoding='utf-8') as f:
        #     json.dump(test_products,f,ensure_ascii=False,indent=2)
        # print("테스트용 JSON 생성 완료")
