from django.shortcuts import render
import json
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger(__name__)
from sklearn.metrics.pairwise import cosine_similarity

# Create your views here.
# def my_item_recommendation(request):
#     # Get recommended or default products
#     search_results = get_top_liked_products(limit=10)
#     recommended_items = []  # Set this if you want a separate recommended section
#     print("....",search_results)

#     return render(
#         request,
#         'upload/upload.html',
#         {
#             'search_results': search_results,
#             'recommended_items': recommended_items
#         }
#     )

def get_recommendation_list():
        # JSON 데이터를 파싱 (실제로는 DB나 API에서 받아올 수 있음)
    products_path = 'static/data/advertise_products.json'
    with open(products_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 태그 추출 규칙 예시 (첫번째 flag 사용 or None)
    def get_tag(flags):
        for tag in ['글로시', 'matte', 'glossy', '증정', '세일', '쿠폰', '오늘드림']:
            if tag in flags:
                return tag
        return flags[0] if flags else '-'

    search_results = [
        {
            "brand": item["brand_name"],
            "name": item["product_name"],
            "image": item["image_src"],
            "price": item["price_original"].replace("~", ""),
            "tag": get_tag(item.get("flags", [])),
            "url": item["product_url"],
        }
        for item in raw_data
    ]
    return search_results

def my_item_recommendation(request):
    search_results = get_recommendation_list()
    return render(request, 'upload/upload.html', {
        "search_results": search_results
    })


@csrf_exempt
def recommend_by_color(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        body = json.loads(request.body)
        warm = body.get("warmCool")
        deep = body.get("lightDeep")
        lab_l = body.get("lab_l", 0)
        lab_a = body.get("lab_a", 0)
        lab_b = body.get("lab_b", 0)

        if warm is None or deep is None:
            return JsonResponse({"error": "Missing coordinates"}, status=400)

        coord = np.array([warm, deep, lab_l, lab_a, lab_b])
        logger.info(f"Received coordinates: warmCool={warm}, lightDeep={deep}, lab_l={lab_l}, lab_a={lab_a}, lab_b={lab_b}")
        import os
        from django.conf import settings
        with open("static/data/cluster_centers.json", "r") as f:
            centers = json.load(f)
        # path = os.path.join(settings.MEDIA_ROOT, 'data', 'cluster_centers.json')
        # with open(path, "r", encoding="utf-8") as f:
        #     centers = json.load(f)
        with open("static/data/products_clustered.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        # path = os.path.join(settings.MEDIA_ROOT, 'data', 'products_clustered.json')
        # with open(path, "r", encoding="utf-8") as f:
        #     products = json.load(f)

        # Step 1: Find closest cluster
        cluster_idx = np.argmin([np.linalg.norm(coord - np.array(c)) for c in centers])
        logger.info(f"Closest cluster index: {cluster_idx}")

        # Step 2: Gather products from the cluster
        cluster_products = [p for p in products if p.get("cluster") == cluster_idx]

        # Step 3: Feature vector comparison (WarmCool, LightDeep, lab_l, lab_a, lab_b)
        def get_feature_vec(p):
            return np.array([
                p.get("warmCool", 0),
                p.get("lightDeep", 0),
                p.get("lab_l", 0),
                p.get("lab_a", 0),
                p.get("lab_b", 0),
            ])

        if len(cluster_products) >= 5:
            candidates = cluster_products
            logger.info(f"Cluster size sufficient: {len(candidates)} candidates")
        else:
            candidates = products
            logger.warning(f"Cluster {cluster_idx} has only {len(cluster_products)} products — using full dataset")

        similarities = []
        for p in candidates:
            prod_vec = get_feature_vec(p).reshape(1, -1)
            user_vec_for_similarity = np.array([
                warm,
                deep,
                p.get("lab_l", 0),
                p.get("lab_a", 0),
                p.get("lab_b", 0),
            ]).reshape(1, -1)

            sim = cosine_similarity(user_vec_for_similarity, prod_vec)[0][0]
            similarities.append((p, sim))

        # Step 4: Sort by cosine similarity (higher is better)
        top_matches = sorted(similarities, key=lambda x: -x[1])[:5]

        # Step 5: Format response
        response = []
        for product, sim in top_matches:
            response.append({
                "id": product.get("id"),  # 제품 ID 추가
                "name": product.get("name"),
                "color_name": product.get("color_name"),
                "hex": product.get("hex"),
                "image": product.get("image"),
                "price": product.get("price"),
                "url": product.get("url"),
                "brand": product.get("brand"),
                "category": product.get("category"),
                "warmCool": product.get("warmCool"),
                "lightDeep": product.get("lightDeep"),
                "distance": round(sim, 4),  # Cosine similarity score
            })

        return JsonResponse({"recommended": response}, json_dumps_params={"ensure_ascii": False})

    except Exception as e:
        logger.exception("Recommendation error")
        return JsonResponse({"error": str(e)}, status=500)