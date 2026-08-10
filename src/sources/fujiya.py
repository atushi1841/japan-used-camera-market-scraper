import asyncio
import random
import re
import datetime
from bs4 import BeautifulSoup

BASE_URL = "https://www.fujiya-camera.co.jp"

CAMERA_CATEGORIES = {
    "rC-CAMMIR": "ミラーレスカメラ",
    "rC-CAMREF": "デジタル一眼レフ",
    "rC-CAMRAN": "デジタルレンジファインダー",
    "rC-CAMMID": "中判デジタル",
    "rC-CAMPNS": "コンパクトデジタル",
    "rC-FCMRAN": "レンジファインダー(フィルム)",
    "rC-FCMMID": "中判カメラ(フィルム)",
    "rC-FCMPNS": "コンパクトカメラ(フィルム)",
    "rC-LENMIR": "ミラーレス用レンズ",
    "rC-LENREF": "一眼レフ用レンズ",
}

async def fetch_fujiya(client, keyword="", max_pages=2, max_items=100):
    results = []
    for code, label in CAMERA_CATEGORIES.items():
        if len(results) >= max_items:
            break
        first_url = f"{BASE_URL}/shop/e/ec-usednw_{code}/"
        page_urls = [first_url] + [
            f"{BASE_URL}/shop/e/ec-usednw_{code}_p{p}/?ps=50"
            for p in range(2, max_pages + 1)
        ]
        for page_index, url in enumerate(page_urls):
            if len(results) >= max_items:
                break

            resp = await client.get(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("dl.block-thumbnail-t--goods")
            if not cards:
                break

            for card in cards:
                if len(results) >= max_items:
                    break

                name_el = card.select_one(".block-thumbnail-t--goods-name")
                if not name_el:
                    continue
                title = name_el.get_text(strip=True)

                if keyword and keyword.lower() not in title.lower():
                    continue

                price_el = card.select_one(".block-thumbnail-t--price")
                price_text = price_el.get_text(strip=True) if price_el else ""
                price = _extract_price(price_text)

                a = card.select_one('a[href*="/shop/g/"]')
                product_url = ""
                product_id = ""
                if a:
                    href = a.get("href", "")
                    if href.startswith("/"):
                        product_url = f"{BASE_URL}{href}"
                    else:
                        product_url = href
                    m = re.search(r"/shop/g/([^/]+)", href)
                    if m:
                        product_id = m.group(1)

                img = card.select_one("img")
                img_url = ""
                if img:
                    src = img.get("data-src") or img.get("src") or ""
                    if src.startswith("data:"):
                        src = ""
                    if src.startswith("/"):
                        img_url = f"{BASE_URL}{src}"

                brand_el = card.select_one("a.js-enhanced-ecommerce-goods-name")
                brand = ""
                if brand_el:
                    brand = brand_el.get("data-brand") or ""

                item = {
                    "productId": product_id,
                    "title": title,
                    "price": price,
                    "brand": brand,
                    "shop": "Fujiya Camera",
                    "category": label,
                    "condition": "中古",
                    "source": "fujiya",
                    "imageUrl": img_url,
                    "productUrl": product_url,
                    "scrapedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }
                results.append(item)

            await asyncio.sleep(random.uniform(1, 3))

    return results[:max_items]

def _extract_price(text):
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None
