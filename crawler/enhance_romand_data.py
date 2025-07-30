import json
import requests
from io import BytesIO
from PIL import Image
import numpy as np
from skimage import color

# Load original data
with open('static/data/romand_products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

enhanced_data = []

for item in data:
    name = item['name']
    image_url = item['image']

    # 1. color_name
    color_name = name.split('/')[-1].strip()

    # 2. category
    category = name.replace("롬앤", "").split('/')[0].strip()

    # 3. brand
    brand = "롬앤"

    # 4. hex + lab (extract average color)
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        img = img.resize((50, 50))  # small size to average
        avg_color = np.array(img).mean(axis=(0, 1))  # R, G, B

        # HEX
        r, g, b = map(int, avg_color)
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)

        # LAB
        rgb_norm = np.array([[avg_color]]) / 255.0
        lab = color.rgb2lab(rgb_norm)[0][0]
        lab_l, lab_a, lab_b = lab.round(2)

    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        hex_color = "#000000"
        lab_l, lab_a, lab_b = 0, 0, 0

    # Add all fields
    item.update({
        "color_name": color_name,
        "category": category,
        "brand": brand,
        "hex": hex_color,
        "lab_l": lab_l,
        "lab_a": lab_a,
        "lab_b": lab_b
    })

    enhanced_data.append(item)

# Save to new file
with open('static/data/romand_products_enhanced.json', 'w', encoding='utf-8') as f:
    json.dump(enhanced_data, f, ensure_ascii=False, indent=2)

print("Done: enhanced data saved.")
