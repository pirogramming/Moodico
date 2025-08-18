# utils/scraper.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_oliveyoung_products(max_items=10):
    # Chrome config
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )

    # Browser 시작
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    products = []

    try:
        # Target
        url = (
            "https://www.oliveyoung.co.kr/store/main/getBestList.do"
            "?dispCatNo=900000100100001&fltDispCatNo=10000010002&pageIdx=1&rowsPerPage=10"
        )
        driver.get(url)

        wait = WebDriverWait(driver, 5) # 5초 기다리기 (아이템들 있는지 체크하는 동안)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.cate_prd_list")))
        items = driver.find_elements(By.CSS_SELECTOR, "ul.cate_prd_list li") #all <li>

        # Hard cap at max_items
        for item in items[:max_items]:
            try:
                # 제품 정보
                prd_info = item.find_element(By.CSS_SELECTOR, "div.prd_info")
                link_tag = prd_info.find_element(By.CSS_SELECTOR, "a.prd_thumb")
                product_url = link_tag.get_attribute("href")
                # 제품 이미지
                img_tag = link_tag.find_element(By.TAG_NAME, "img")
                image_src = img_tag.get_attribute("src") or img_tag.get_attribute("data-original") or ""
                image_alt = img_tag.get_attribute("alt") or ""

                brand_name = prd_info.find_element(By.CSS_SELECTOR, "span.tx_brand").text.strip()
                product_name = prd_info.find_element(By.CSS_SELECTOR, "p.tx_name").text.strip()
                price_original = prd_info.find_element(By.CSS_SELECTOR, "p.prd_price span.tx_org").text.strip()

                # 제품 태크들
                flags = []
                try:
                    flag_spans = prd_info.find_elements(By.CSS_SELECTOR, "p.prd_flag span.icon_flag")
                    flags = [flag.text.strip() for flag in flag_spans if flag.text.strip()]
                except Exception:
                    pass

                products.append({
                    "product_url": product_url,
                    "brand_name": brand_name,
                    "product_name": product_name,
                    "image_src": image_src,
                    "image_alt": image_alt,
                    "price_original": price_original,
                    "flags": flags,
                })

                if len(products) >= max_items:
                    break
            except Exception:
                continue
    finally:
        driver.quit()

    return products
