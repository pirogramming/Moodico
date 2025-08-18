import json, os
from django.shortcuts import render
from django.conf import settings
from ..models import ProductLike

def get_top_liked_products(limit=10, include_unliked=True, category=None):
    """
    상위 찜 제품 조회
    """
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except FileNotFoundError:
        return []

    all_products_by_id = {str(p["id"]): p for p in all_products if "id" in p}

    # 좋아요 집계
    product_likes_summary = {}
    for item in ProductLike.objects.all():
        pid = str(item.product_id)
        if pid in all_products_by_id:
            if pid not in product_likes_summary:
                product = all_products_by_id[pid]
                product_likes_summary[pid] = {
                    'product_id': pid,
                    'product_name': product.get("name", ""),
                    'product_brand': product.get("brand", ""),
                    'product_price': product.get("price", ""),
                    'product_image': product.get("image", ""),
                    'product_category': product.get("category", ""),
                    'like_count': 0
                }
            product_likes_summary[pid]['like_count'] += 1

    products_with_likes = list(product_likes_summary.values())

    # 좋아요 없는 제품 포함
    if include_unliked:
        liked_ids = set(product_likes_summary.keys())
        for pid, product in all_products_by_id.items():
            if pid not in liked_ids:
                products_with_likes.append({
                    'product_id': pid,
                    'product_name': product.get("name", ""),
                    'product_brand': product.get("brand", ""),
                    'product_price': product.get("price", ""),
                    'product_image': product.get("image", ""),
                    'product_category': product.get("category", ""),
                    'like_count': 0
                })

    # 카테고리 필터링
    if category:
        category_lower = category.strip().lower()
        products_with_likes = [
            p for p in products_with_likes
            if p.get('product_category', '').strip().lower() == category_lower
        ]

    # 정렬
    products_with_likes.sort(key=lambda x: (-x['like_count'], x['product_name']))
    return products_with_likes[:limit]