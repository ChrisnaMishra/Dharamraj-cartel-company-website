#!/usr/bin/env python3
"""Build the Dharamraj Cartel local product-detail catalogue from Indigo's public product pages."""
import json, re, time
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "indigo_images" / "products.json"
OUTPUT = ROOT / "indigo_images" / "product-details.json"
HEADERS = {"User-Agent": "DharamrajCartelProductCatalogue/1.0 (product detail sync)"}

def clean_text(node):
    if not node:
        return ""
    for bad in node.select("script, style, noscript, iframe, button, .share, .social"):
        bad.decompose()
    return re.sub(r"\n{3,}", "\n\n", node.get_text("\n", strip=True)).strip()

def parse_product(url, fallback, category, session):
    response = session.get(url, timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title_node = soup.select_one("h1.product_title, h1.entry-title, main h1, h1")
    name = clean_text(title_node) or fallback.get("name", "Kitchenware product")

    description_node = soup.select_one(".woocommerce-Tabs-panel--description, #tab-description, .woocommerce-product-details__short-description")
    if not description_node:
        description_node = soup.select_one(".product .summary")
    description = clean_text(description_node)
    description = re.sub(r"\b(Add to cart|Shopping Basket)\b.*$", "", description, flags=re.I | re.S).strip()

    specifications = []
    for table in soup.select(".woocommerce-product-details__short-description table, #tab-description table, .woocommerce-Tabs-panel--description table, .product table, table"):
        for tr in table.select("tr"):
            cells = [clean_text(cell) for cell in tr.select("th, td")]
            cells = [cell for cell in cells if cell]
            if len(cells) >= 2 and cells not in specifications:
                specifications.append(cells[:4])

    features = []
    desc_root = description_node or soup
    for li in desc_root.select("li"):
        value = clean_text(li)
        if value and value not in features and len(value) < 260:
            features.append(value)
    if not features:
        # Some supplier pages use bold feature headings and paragraphs rather than lists.
        for p in desc_root.select("p"):
            value = clean_text(p)
            if value and value.lower() not in (name.lower(), "description") and len(value) < 260:
                features.append(value)
            if len(features) >= 8:
                break

    image_urls = list(fallback.get("image_urls") or [])
    for image in soup.select(".woocommerce-product-gallery img, .wp-post-image"):
        src = image.get("data-large_image") or image.get("data-src") or image.get("src")
        if src and src.startswith("http") and src not in image_urls:
            image_urls.append(src)
    category_nodes = [clean_text(x) for x in soup.select(".posted_in a, .tagged_as a")]
    product = {
        "name": name,
        "category": category,
        "url": url,
        "description": description[:6500],
        "specifications": specifications[:40],
        "features": features[:20],
        "image_urls": image_urls[:12],
        "supplier_categories": category_nodes,
        "source": "Indigo Metalware LLP",
    }
    return product

def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update(HEADERS)
    results = {}
    products = [(group.get("name", "Kitchenware"), item) for group in manifest.get("categories", []) for item in group.get("products", [])]
    failures = []
    for index, (category, item) in enumerate(products, 1):
        url = item.get("url")
        if not url:
            continue
        try:
            results[url] = parse_product(url, item, category, session)
            print(f"[{index}/{len(products)}] OK {results[url]['name']}")
        except Exception as exc:
            failures.append({"url": url, "name": item.get("name", ""), "error": str(exc)[:300]})
            # Keep the product available even if the supplier page temporarily fails.
            results[url] = {
                "name": item.get("name", "Kitchenware product"),
                "category": category,
                "url": url,
                "description": "",
                "specifications": [],
                "features": [],
                "image_urls": item.get("image_urls", []),
                "supplier_categories": [],
                "source": "Indigo Metalware LLP",
                "sync_error": str(exc)[:300],
            }
            print(f"[{index}/{len(products)}] FAILED {url}: {exc}")
        time.sleep(0.2)
    payload = {
        "source": manifest.get("source", "https://indigometal.com/household/"),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "product_count": len(results),
        "failed_count": len(failures),
        "products": results,
        "failures": failures,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} product records to {OUTPUT}; {len(failures)} pages failed.")

if __name__ == "__main__":
    main()
