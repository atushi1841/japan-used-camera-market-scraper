import asyncio
import json
import sys
import datetime
import unicodedata
import httpx

def _norm_key(text):
    return unicodedata.normalize("NFC", text).casefold()

try:
    from apify import Actor
except Exception:
    Actor = None

async def main():
    if Actor is not None:
        async with Actor:
            actor_input = await Actor.get_input() or {}
            await run(actor_input, actor=Actor)
    else:
        raw = sys.stdin.read() or ""
        try:
            actor_input = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            actor_input = {}
        await run(actor_input, actor=None)

async def run(actor_input, actor=None):
    search_keyword = actor_input.get("searchKeyword") or ""
    max_items = int(actor_input.get("maxItems", 100))
    max_pages = int(actor_input.get("maxPages", 2))
    sources = [s.strip() for s in actor_input.get("sources", "kitamura,fujiya").split(",") if s.strip()]
    stats_mode = actor_input.get("statsMode", False)
    collected_items = []

    proxy_url = None
    if actor is not None:
        proxy_config = await actor.create_proxy_configuration(actor_proxy_input=actor_input.get("proxyConfiguration"))
        if proxy_config:
            proxy_url = await proxy_config.new_url()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    }

    # キタムラAPIはApifyプロキシ(海外DC IP)を403ブロックするため、プロキシなしでアクセスする
    # フジヤはSSRページのためプロキシ使用OK
    async with httpx.AsyncClient(proxy=None, headers=headers, timeout=30.0) as client_direct, \
               httpx.AsyncClient(proxy=proxy_url, headers=headers, timeout=30.0) as client_proxy:
        collected = 0
        for src in sources:
            if collected >= max_items:
                break
            remaining = max_items - collected
            items = []
            if src == "kitamura":
                from sources.kitamura import fetch_kitamura
                items = await fetch_kitamura(client_direct, keyword=search_keyword, max_pages=max_pages, max_items=remaining)
            elif src == "fujiya":
                from sources.fujiya import fetch_fujiya
                items = await fetch_fujiya(client_proxy, keyword=search_keyword, max_pages=max_pages, max_items=remaining)

            for item in items:
                if stats_mode:
                    collected_items.append(item)
                else:
                    if actor is not None:
                        await actor.push_data(item)
                    else:
                        print(json.dumps(item, ensure_ascii=False))
                collected += 1
                if collected >= max_items:
                    break

        if stats_mode:
            stats_keyword = actor_input.get("statsKeyword") or ""
            filtered_items = collected_items
            if stats_keyword:
                nk = _norm_key(stats_keyword)
                filtered_items = [it for it in collected_items if nk in _norm_key(it.get("title", ""))]
            prices = []
            for it in filtered_items:
                try:
                    p = int(it.get("price", 0))
                except (TypeError, ValueError):
                    continue
                if p > 0:
                    prices.append(p)
            count = len(prices)
            if count == 0:
                price_min = 0
                price_max = 0
                price_avg = 0
                price_median = 0
                sample = []
            else:
                price_min = min(prices)
                price_max = max(prices)
                price_avg = int(sum(prices) / count)
                sorted_prices = sorted(prices)
                mid = count // 2
                if count % 2 == 0:
                    price_median = int((sorted_prices[mid - 1] + sorted_prices[mid]) / 2)
                else:
                    price_median = sorted_prices[mid]
                sample = []
                for it in filtered_items[:3]:
                    sample.append({
                        "title": it.get("title", ""),
                        "price": it.get("price", 0),
                        "detailUrl": it.get("detailUrl", ""),
                        "shop": it.get("shop", "")
                    })
            stats_result = {
                "statsType": "japan-camera-price",
                "keyword": stats_keyword if stats_keyword else search_keyword,
                "count": count,
                "priceMin": price_min,
                "priceMax": price_max,
                "priceAvg": price_avg,
                "priceMedian": price_median,
                "sampleItems": sample,
                "collectedAt": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
            }
            if actor is not None:
                await actor.push_data(stats_result)
            else:
                print(json.dumps(stats_result, ensure_ascii=False))
            return

if __name__ == "__main__":
    asyncio.run(main())
