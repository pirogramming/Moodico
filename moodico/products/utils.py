from moodico.products.models import ProductLike

def get_top_liked_products(limit=10, include_unliked=True):
    """
    상위 찜 제품 조회 함수
    - include_unliked: True면 좋아요 없는 제품도 포함
    """
    import json
    import os
    from django.conf import settings

    # 전체 제품 데이터 로드
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except FileNotFoundError:
        print("all_products.json 파일을 찾을 수 없습니다.")
        return []

    # id로 빠른 접근을 위해 dict로 변환
    all_products_by_id = {str(p["id"]): p for p in all_products if "id" in p and p["id"]}

    # 1) 찜 개수 집계 (id 기준)
    product_likes_summary = {}
    for item in ProductLike.objects.all():
        pid = str(item.product_id)
        if pid in all_products_by_id:  # only include products with real id from all_products.json
            if pid not in product_likes_summary:
                product = all_products_by_id[pid]
                product_likes_summary[pid] = {
                    'product_id': pid,
                    'product_name': product.get("name", ""),
                    'product_brand': product.get("brand", ""),
                    'product_price': product.get("price", ""),
                    'product_image': product.get("image", ""),
                    'like_count': 0
                }
            product_likes_summary[pid]['like_count'] += 1

    products_with_likes = list(product_likes_summary.values())

    # 2) 좋아요 없는 모든 제품 포함 (옵션)
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
                    'like_count': 0
                })

    # 3) 정렬
    products_with_likes.sort(key=lambda x: (-x['like_count'], x['product_name']))
    return products_with_likes[:limit]