# moodico/products/management/commands/scrape_products.py

## 실행방법
'''
python manage.py scrape_products --brands romand,3ce --scroll 4 --limit 5
'''
import os
import time
import json
import uuid
import requests
import numpy as np
from io import BytesIO
from PIL import Image
from skimage import color

from django.core.management.base import BaseCommand
from django.conf import settings

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


TARGETS_DEFAULT = [
    {"brand": "romand", "url": "https://romand.co.kr/product/maincatedetail.html?cate_code=289", "category": "Lips"},
    {"brand": "3ce",   "url": "https://www.3cecosmetics.com/all-products/lips",            "category": "Lips"},
    {"brand": "3ce",   "url": "https://www.3cecosmetics.com/all-products/cheeks/blush",    "category": "blush"},
    {"brand": "3ce",   "url": "https://www.3cecosmetics.com/all-products/eyes/eyeshadow",  "category": "eyeshadow"},
]

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
    """Remove near-white background, compute average color; return (hex, L, a, b)."""
    try:
        response = requests.get(img_url, timeout=8)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert('RGB')
        img = img.resize((50, 50))
        pixels = np.array(img).reshape(-1, 3)

        # filter out very bright pixels (likely background)
        filtered = [px for px in pixels if not all(c > 240 for c in px)]
        if not filtered:
            filtered = pixels

        avg_rgb = np.array(filtered).mean(axis=0)
        r, g, b = map(int, avg_rgb)
        hex_code = '#{:02x}{:02x}{:02x}'.format(r, g, b)

        rgb_norm = np.array([[avg_rgb]]) / 255.0
        lab = color.rgb2lab(rgb_norm)[0][0]
        lab_l, lab_a, lab_b = lab.round(2)

        return hex_code, float(lab_l), float(lab_a), float(lab_b)
    except Exception as e:
        print(f"[Color Error] {img_url} - {e}")
        return "#000000", 0.0, 0.0, 0.0


class Command(BaseCommand):
    help = "Scrape cosmetic products and dump a JSON file under MEDIA_ROOT/data/test_products.json"

    def add_arguments(self, parser):
        parser.add_argument("--scroll", type=int, default=4, help="Scroll count per page (default: 4)")
        parser.add_argument("--headful", action="store_true", help="Run Chrome with UI (not headless)")
        parser.add_argument("--output", default="data/test_products.json",
                            help="Output path under MEDIA_ROOT (default: data/test_products.json)")
        parser.add_argument("--limit", type=int, default=10,
                            help="Number of examples to keep in test JSON (first N + last N, default: 10)")
        parser.add_argument("--brands", default="romand,3ce",
                            help="Comma-separated brands to scrape (romand,3ce). Default: both")

    def handle(self, *args, **opts):
        scroll_count = opts["scroll"]
        headless = not opts["headful"]
        brands = {b.strip().lower() for b in opts["brands"].split(",") if b.strip()}
        output_rel = opts["output"]
        test_limit = max(1, int(opts["limit"]))

        # Selenium options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Driver (downloads matching ChromeDriver if needed)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Targets
        targets = [t for t in TARGETS_DEFAULT if t["brand"].lower() in brands]

        all_products = []
        try:
            for target in targets:
                brand = target["brand"]
                url = target["url"]
                category = target["category"]
                self.stdout.write(f"Scraping {brand} ({category}) ...")

                driver.get(url)
                time.sleep(2)

                for _ in range(scroll_count):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                if brand.lower() == "romand":
                    raw_items = extract_romand_items(driver, category)
                elif brand.lower() == "3ce":
                    raw_items = extract_3ce_items(driver, category)
                else:
                    self.stdout.write(self.style.WARNING(f"No extractor for: {brand}"))
                    continue

                self.stdout.write(f"  → {len(raw_items)} items found")

                # enrich with color
                for item in raw_items:
                    hex_color, lab_l, lab_a, lab_b = extract_average_color(item["image"])
                    product = {
                        "id": str(uuid.uuid4()),
                        **item,
                        "hex": hex_color,
                        "lab_l": lab_l,
                        "lab_a": lab_a,
                        "lab_b": lab_b,
                    }
                    all_products.append(product)
        finally:
            driver.quit()

        # Save under MEDIA_ROOT/data/...
        out_path = os.path.join(settings.MEDIA_ROOT, output_rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        # keep a small test set (first N + last N)
        test_products = all_products[:test_limit] + all_products[-test_limit:]

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(test_products, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"Saved {len(test_products)} items to {out_path} (from {len(all_products)} scraped)"))
