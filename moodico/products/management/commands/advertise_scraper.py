import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class Command(BaseCommand):
    help = "Scrape products and save JSON under STATIC_ROOT/data/advertise_products.json"

    def handle(self, *args, **options):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        )

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        try:
            url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo=10000010002&pageIdx=1&rowsPerPage=10"
            driver.get(url)
            wait = WebDriverWait(driver, 15)

            # Wait for <ul class="cate_prd_list"> to appear (parent of products)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.cate_prd_list')))
            # Now get all <li class="flag">
            products = driver.find_elements(By.CSS_SELECTOR, 'li.flag')

            all_products = []
            for item in products:
                try:
                    prd_info = item.find_element(By.CSS_SELECTOR, 'div.prd_info')

                    # Main image and link
                    link_tag = prd_info.find_element(By.CSS_SELECTOR, 'a.prd_thumb')
                    product_url = link_tag.get_attribute('href')
                    img_tag = link_tag.find_element(By.TAG_NAME, 'img')
                    image_src = img_tag.get_attribute('src')
                    image_alt = img_tag.get_attribute('alt')

                    # Brand and product name
                    prd_name_box = prd_info.find_element(By.CSS_SELECTOR, 'div.prd_name')
                    brand_name = ''
                    product_name = ''
                    try:
                        brand_name = prd_name_box.find_element(By.CSS_SELECTOR, 'span.tx_brand').text.strip()
                    except Exception:
                        pass
                    try:
                        product_name = prd_name_box.find_element(By.CSS_SELECTOR, 'p.tx_name').text.strip()
                    except Exception:
                        pass

                    # Price
                    price_original = ''
                    price_current = ''
                    try:
                        price_box = prd_info.find_element(By.CSS_SELECTOR, 'p.prd_price')
                        price_original_elem = price_box.find_elements(By.CSS_SELECTOR, 'span.tx_org')
                        price_original = price_original_elem[0].text.strip() if price_original_elem else ''
                        price_current_elem = price_box.find_elements(By.CSS_SELECTOR, 'span.tx_cur')
                        price_current = price_current_elem.text.strip() if price_current_elem else ''
                    except Exception:
                        pass

                    # Flags
                    flags = []
                    try:
                        prd_flag_box = prd_info.find_element(By.CSS_SELECTOR, 'p.prd_flag')
                        flag_spans = prd_flag_box.find_elements(By.CSS_SELECTOR, 'span.icon_flag')
                        flags = [flag.text.strip() for flag in flag_spans]
                    except Exception:
                        pass

                    # Review score
                    review_score = None
                    try:
                        prd_point_box = prd_info.find_element(By.CSS_SELECTOR, 'p.prd_point_area')
                        review_point_elem = prd_point_box.find_elements(By.CSS_SELECTOR, 'span.review_point')
                        if review_point_elem:
                            score_text = review_point_elem[0].text.strip()
                            if '10점만점에' in score_text and '점' in score_text:
                                review_score = score_text.replace('10점만점에', '').replace('점', '').strip()
                    except Exception:
                        pass

                    product_data = {
                        'product_url': product_url,
                        'brand_name': brand_name,
                        'product_name': product_name,
                        'image_src': image_src,
                        'image_alt': image_alt,
                        'price_original': price_original,
                        'price_current': price_current,
                        'flags': flags,
                        'review_score': review_score
                    }

                    all_products.append(product_data)
                except Exception as e:
                    self.stderr.write(f"Error scraping item: {e}")
                    continue
                
            SAVE_PATH = os.path.join(settings.BASE_DIR, 'static', 'data', 'advertise_products.json')
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            with open(SAVE_PATH, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            print(f"\nSaved {len(all_products)} products to {SAVE_PATH}")

        finally:
            driver.quit()
