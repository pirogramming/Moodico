import json
import random
import math
import logging
logger = logging.getLogger(__name__)

def product_result_by_mood(mood):
    try:
        mood_zones_path = 'static/data/mood_zones.json'
        products_path = 'static/data/all_products.json'

        with open(mood_zones_path, 'r', encoding='utf-8') as f:
            mood_zones = json.load(f)
        
        with open(products_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
        
        zone = mood_zones[mood]['area']
        zone_left = zone['left']
        zone_top = zone['top']
        zone_right = zone_left + zone['width']
        zone_bottom = zone_top + zone['height']

        filtered_results = []
        for product in all_products:
            # LAB -> coords 변환 로직
            coords = calculate_coordinates_from_lab(product['lab_l'], product['lab_a'], product['lab_b'])

            if (zone_left <= coords['warmCool'] <= zone_right and
                zone_top <= coords['lightDeep'] <= zone_bottom):
                filtered_results.append(product)
            
        return filtered_results
    
    except Exception as e:
        # logger.error(f"제품 필터링 중 에러 발생: {e}")
        return []

# 무드필터링 된 제품을 받아서 랜덤으로 최대 3개 반환하는 함수
# 우선은 랜덤으로 구현하였으나, 로직 수정 가능
def get_random_products(filtered_products):
    product_count = len(filtered_products)
    if product_count > 3:
        return random.sample(filtered_products, 3)
    else:
        return filtered_products

# color_analyzer.js의 calculateCoordinatesFromLAB(l, a, b)와 동일한 역할의 함수
def sigmoid(x):
    return 1 / (1 + math.exp(-x))
def enhance_contrast(value):
    return (1 - math.cos(value * math.pi)) / 2
def calculate_coordinates_from_lab(l, a, b):
    l_star = l
    a_star = a
    b_star = b

    warm_cool_score = (a_star * 0.5) + (b_star * 1.0)

    # sigmoid를 활용한 비선형 매핑 - warmCool
    spread_wc_factor = 35
    scaled_wc_score = (warm_cool_score - 35) / spread_wc_factor
    sigmoid_wc_middle_value = sigmoid(scaled_wc_score)
    sigmoid_wc_value = enhance_contrast(sigmoid_wc_middle_value) + 0.03

    # 선형 매핑 간격 조정 - lightDeep
    scale = 1.1
    offset = -7
    light_score = (l_star * scale) + offset

    light_score = max(0, min(100, light_score))

    warm_cool = sigmoid_wc_value * 100
    light_deep = 100 - light_score

    return {'warmCool': warm_cool, 'lightDeep': light_deep}
