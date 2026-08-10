import asyncio
import random
import datetime
import httpx

API_URL = "https://shop.kitamura.jp/ec/api/cache/s/v1/used_sell_search"

async def fetch_kitamura(client, keyword="", max_pages=2, max_items=100):
    results = []
    offset = 1
    size = min(80, max_items)
    page = 0
    while page < max_pages and len(results) < max_items:
        params = {
            "sort": "default",
            "size": size,
            "offset": offset,
            "func": "srch",
            "ref_id": "used_sell_search",
            "extra_fields": "sales_status,is_maintenance,sale_start_at,sale_end_at",
            "site": "ns",
            "is_logged_in": "0",
            "aggs": "default",
        }
        if keyword:
            params["query"] = keyword

        resp = await client.get(API_URL, params=params)
        data = resp.json()
        hits = (data.get("search") or {}).get("hits") or []
        if not hits:
            break

        for hit in hits:
            item = {
                "productId": hit.get("id"),
                "title": hit.get("title", ""),
                "price": hit.get("price"),
                "brand": hit.get("maker", ""),
                "shop": hit.get("shop", ""),
                "category": hit.get("category", []),
                "imageUrl": hit.get("image_link", ""),
                "productUrl": f"https://shop.kitamura.jp/ec/prd/{hit.get('id')}",
                "condition": "",
                "source": "kitamura",
                "scrapedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            results.append(item)
            if len(results) >= max_items:
                break

        offset += size
        page += 1
        if len(hits) < size:
            break
        await asyncio.sleep(random.uniform(1, 3))

    return results[:max_items]
