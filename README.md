# Japan Used Camera Market — Cross-Shop Price Comparison

**Compare used camera & lens prices across Japan's largest used-camera retailers in a single dataset.**

Scrapes listings from **Kitamura (キタムラ)** — Japan's biggest used-camera chain (300+ stores) — and **Fujiya Camera (フジヤカメラ)** — Tokyo's legendary used-camera specialist (since 1938). Each item is tagged with its `source` and `shop` so you can compare prices for the same model across shops.

## Why this is useful

- **Cross-shop price comparison** — the same lens/camera often differs by 10-30% between shops
- **Resale arbitrage** — find underpriced gear at one shop, sell at another
- **Price monitoring** — track market moves for your gear before buying/selling
- **Full market scan** — one run covers all camera categories: mirrorless, DSLR, rangefinder, medium format, compact, and lenses

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchKeyword` | string | `α7` | Keyword filter (empty = full market scan) |
| `maxItems` | integer | 100 | Max items to collect |
| `maxPages` | integer | 2 | Max pages per source |
| `sources` | string | `kitamura,fujiya` | Comma-separated source list |

## Output fields

| Field | Description |
|---|---|
| `productId` | Product ID at source shop |
| `title` | Product title |
| `price` | Price in JPY |
| `brand` | Brand / maker |
| `shop` | Source shop name |
| `category` | Category label |
| `condition` | Condition (`中古` for used) |
| `source` | `kitamura` or `fujiya` |
| `imageUrl` | Product image URL |
| `productUrl` | Product page URL |
| `scrapedAt` | Scrape timestamp |

## Output sample

```json
{
  "productId": "2445650064817",
  "title": "ソニー α7III ボディ [ILCE-7M3]",
  "price": 130600,
  "brand": "ソニー",
  "shop": "東京・二子玉川店",
  "category": [
    "ミラーレス一眼:メーカーで選ぶ:ソニー",
    "ミラーレス一眼:センサーサイズで選ぶ:フルサイズ以上",
    "ミラーレス一眼:本体質量で選ぶ:300g～"
  ],
  "imageUrl": "https://nc-img.kitamura.jp/2445650064817-1-1.jpg",
  "productUrl": "https://shop.kitamura.jp/ec/prd/2445650064817",
  "condition": "",
  "source": "kitamura",
  "scrapedAt": "2026-08-10T09:54:24.973364+00:00"
}
```

The `source` + `shop` fields let you compare the same model across shops: run once with `searchKeyword: "α7"` and get Kitamura and Fujiya prices side by side.

## Pricing

Pay per event — $0.00005/run + **$0.002/item**.

## Data source notes

- **Kitamura**: official public search API (`used_sell_search`), 300+ store chain, ~40k used items
- **Fujiya Camera**: server-side rendered category pages (used section), 486+ used items in camera categories alone

Both sources are public web data; only factual product information (name, price, brand, stock status) is collected.
