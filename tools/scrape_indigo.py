#!/usr/bin/env python3
"""Collect real Indigo Household product photographs for the Dharamraj Cartel site.

Reads the Household categories from Indigo's public WooCommerce pages, visits
each listed product, downloads its full-size gallery photos, optimises them to
WebP for the website, and writes a local JSON/CSV manifest.

Run locally:
  python -m pip install requests beautifulsoup4 Pillow
  python tools/scrape_indigo.py

The GitHub Actions workflow runs the same script and commits the generated
indigo_images/ folder to the deployment branch. The product photos remain local
assets on the site; visitors do not need to hotlink Indigo for each image.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, UnidentifiedImageError

BASE = "https://indigometal.com"
START = BASE + "/household/"
OUT = Path("indigo_images")
DELAY = 0.65
TIMEOUT = 30
MAX_SIDE = 1200
WEBP_QUALITY = 84
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DharamrajCartelHouseholdCatalogue/1.0)",
    "Accept-Language": "en",
}

CATEGORY_NAMES = [
    "Kitchen Tools",
    "Cookware",
    "Tableware Household",
    "Storage",
    "Cloth Care Essentials",
    "Bowls & Colanders",
    "Dustbins",
    "Imported Items",
    "Hot Case & Tea Urn",
    "Cutlery",
]
CATEGORY_SLUGS = {
    "Kitchen Tools": "kitchen-tools",
    "Cookware": "cookware",
    "Tableware Household": "tableware-household",
    "Storage": "storage",
    "Cloth Care Essentials": "cloth-care-essentials",
    "Bowls & Colanders": "bowls-colanders",
    "Dustbins": "dustbins",
    "Imported Items": "imported-items",
    "Hot Case & Tea Urn": "hot-case-tea-urn",
    "Cutlery": "cutlery",
}
NAME_LOOKUP = {
    re.sub(r"[^a-z0-9]+", " ", name.lower()).strip(): name
    for name in CATEGORY_NAMES
}
FALLBACK_CATEGORY_URLS = {
    name: f"{BASE}/product-category/{slug}/"
    for name, slug in CATEGORY_SLUGS.items()
}

session = requests.Session()
session.headers.update(HEADERS)


def canonical_category(text: str) -> str | None:
    key = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return NAME_LOOKUP.get(key)


def get(url: str) -> requests.Response | None:
    """GET with retries and a small delay between requests."""
    for attempt in range(3):
        try:
            response = session.get(url, timeout=TIMEOUT)
            if response.status_code == 404:
                time.sleep(0.15)
                return None
            response.raise_for_status()
            time.sleep(DELAY)
            return response
        except requests.RequestException as error:
            print(f"   retry {attempt + 1}/3 for {url}: {error}", flush=True)
            time.sleep(1.5 * (attempt + 1))
    return None


def soup_of(url: str) -> BeautifulSoup | None:
    response = get(url)
    if response is None:
        return None
    return BeautifulSoup(response.text, "html.parser")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-") or "item"


SIZE_SUFFIX = re.compile(r"-\d+x\d+(?=\.[a-z0-9]+(?:\?|$))", re.I)


def full_size(url: str) -> str:
    """Convert WordPress thumbnail names like item-402x391.jpg to item.jpg."""
    return SIZE_SUFFIX.sub("", url)


def image_url(tag) -> str | None:
    for attribute in ("data-large_image", "data-src", "data-lazy-src", "src"):
        value = tag.get(attribute)
        if value and not value.startswith("data:"):
            return urljoin(BASE, value)
    return None


def find_categories() -> dict[str, str]:
    """Discover only the ten Household category links, avoiding unrelated ranges."""
    page = soup_of(START)
    found: dict[str, str] = {}
    if page:
        for anchor in page.select('a[href*="/product-category/"]'):
            name = anchor.get_text(" ", strip=True) or anchor.get("title", "")
            category = canonical_category(name)
            if not category:
                continue
            url = urldefrag(urljoin(BASE, anchor["href"].split("?")[0]))[0]
            if not url.endswith("/"):
                url += "/"
            found[category] = url

    categories = {}
    for name in CATEGORY_NAMES:
        categories[name] = found.get(name, FALLBACK_CATEGORY_URLS[name])
    return categories


def list_products(category_url: str) -> dict[str, str]:
    """Return unique product URL -> display name, following WooCommerce pages."""
    products: dict[str, str] = {}
    visited: set[str] = set()
    url: str | None = category_url
    while url and url not in visited:
        visited.add(url)
        page = soup_of(url)
        if page is None:
            break

        for item in page.select("li.product, article.product, .product.type-product"):
            anchor = item.select_one('a[href*="/product/"]')
            if anchor is None:
                continue
            href = urldefrag(urljoin(BASE, anchor["href"].split("?")[0]))[0]
            title = item.select_one(
                ".woocommerce-loop-product__title, h2, h3"
            )
            name = title.get_text(" ", strip=True) if title else anchor.get_text(" ", strip=True)
            if href and "/product/" in urlparse(href).path:
                products.setdefault(href, name or href.rstrip("/").split("/")[-1])

        next_link = page.select_one("a.next.page-numbers, a.next")
        if next_link and next_link.get("href"):
            next_url = urldefrag(urljoin(url, next_link["href"]))[0]
            url = next_url if next_url not in visited else None
        else:
            url = None
    return products


def product_images(product_url: str, fallback_name: str) -> tuple[str, list[str]]:
    """Return a product title and unique full-size WordPress gallery image URLs."""
    page = soup_of(product_url)
    if page is None:
        return fallback_name, []

    title = page.select_one("h1.product_title, h1")
    name = title.get_text(" ", strip=True) if title else fallback_name
    urls: list[str] = []

    # Gallery anchor URLs point at full-size files on normal WooCommerce pages.
    for anchor in page.select(
        ".woocommerce-product-gallery__image a[href], "
        ".woocommerce-product-gallery a[data-large_image]"
    ):
        raw = anchor.get("href") or anchor.get("data-large_image")
        if raw:
            urls.append(urljoin(BASE, raw))

    if not urls:
        for image in page.select(".woocommerce-product-gallery img"):
            url = image_url(image)
            if url:
                urls.append(full_size(url))

    if not urls:
        social = page.select_one('meta[property="og:image"]')
        if social and social.get("content"):
            urls.append(full_size(urljoin(BASE, social["content"])))

    unique: list[str] = []
    seen: set[str] = set()
    for url in urls:
        parsed = urlparse(url)
        if "/wp-content/uploads/" in parsed.path and url not in seen:
            seen.add(url)
            unique.append(url)
    return name, unique


def download_webp(url: str, destination: Path) -> bool:
    """Download an original photo, preserve detail, and save a web-optimised WebP."""
    if destination.exists() and destination.stat().st_size > 0:
        return True
    response = get(url)
    if response is None:
        return False
    try:
        with Image.open(BytesIO(response.content)) as original:
            image = ImageOps.exif_transpose(original)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(
                destination,
                format="WEBP",
                quality=WEBP_QUALITY,
                method=6,
                optimize=True,
            )
        return destination.exists() and destination.stat().st_size > 0
    except (UnidentifiedImageError, OSError, ValueError) as error:
        print(f"   ! image could not be converted: {url} ({error})", flush=True)
        return False


def write_category_cover(category_slug: str, relative_images: list[str], all_images: list[str]) -> None:
    """Create a photo cover per category from its first real product photo."""
    candidates = relative_images or all_images
    if not candidates:
        return
    source = OUT / candidates[0]
    target = OUT / "categories" / f"{category_slug}.webp"
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists() and (not target.exists() or source.stat().st_mtime > target.stat().st_mtime):
        shutil.copy2(source, target)


def create_household_cover(category_cover_paths: list[Path]) -> None:
    """Compose a wide real-product-photo strip for the Home & Kitchen tile."""
    existing = [p for p in category_cover_paths if p.exists()]
    if not existing:
        return
    tile_w, tile_h = 300, 190
    cols = min(5, len(existing))
    rows = min(2, (len(existing) + cols - 1) // cols)
    canvas = Image.new("RGB", (cols * tile_w, rows * tile_h), (242, 242, 240))
    for index, path in enumerate(existing[: cols * rows]):
        try:
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image = ImageOps.fit(image, (tile_w, tile_h), method=Image.Resampling.LANCZOS)
                canvas.paste(image, ((index % cols) * tile_w, (index // cols) * tile_h))
        except (UnidentifiedImageError, OSError, ValueError):
            continue
    target = OUT / "categories" / "household-range.webp"
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, format="WEBP", quality=84, method=6, optimize=True)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    csv_rows: list[list[str]] = []
    grouped: dict[str, list[dict[str, object]]] = {}
    all_relative_images: list[str] = []
    category_covers: list[Path] = []

    categories = find_categories()
    print(f"Found {len(categories)} Household categories", flush=True)

    for category_name in CATEGORY_NAMES:
        category_url = categories[category_name]
        category_slug = CATEGORY_SLUGS[category_name]
        print(f"\n== {category_name}: {category_url}", flush=True)
        products = list_products(category_url)
        print(f"   {len(products)} product listings", flush=True)
        grouped[category_name] = []
        category_images: list[str] = []
        category_dir = OUT / category_slug
        category_dir.mkdir(parents=True, exist_ok=True)

        for product_url, product_name in products.items():
            name, urls = product_images(product_url, product_name)
            saved_images: list[str] = []
            for index, url in enumerate(urls, start=1):
                stem = slugify(name) + (f"-{index}" if index > 1 else "")
                relative = f"{category_slug}/{stem}.webp"
                destination = OUT / relative
                if download_webp(url, destination):
                    saved_images.append(relative)
                    category_images.append(relative)
                    all_relative_images.append(relative)
                    csv_rows.append([
                        category_name, name, f"{OUT.name}/{relative}", url, product_url
                    ])
                    print(f"   ok  {relative}", flush=True)
                else:
                    print(f"   FAIL {url}", flush=True)

            grouped[category_name].append({
                "name": name,
                "images": saved_images,
                "url": product_url,
                "image_urls": urls,
            })
            if not urls:
                csv_rows.append([category_name, name, "", "", product_url])

        write_category_cover(category_slug, category_images, all_relative_images)
        cover = OUT / "categories" / f"{category_slug}.webp"
        if cover.exists():
            category_covers.append(cover)

    create_household_cover(category_covers)

    manifest = {
        "source": START,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": [
            {
                "name": name,
                "slug": CATEGORY_SLUGS[name],
                "url": categories[name],
                "products": grouped[name],
            }
            for name in CATEGORY_NAMES
        ],
    }
    (OUT / "products.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (OUT / "products.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["category", "product", "image_file", "image_url", "product_url"])
        writer.writerows(csv_rows)

    total_products = sum(len(items) for items in grouped.values())
    total_images = len(set(all_relative_images))
    print(
        f"\nFinished: {total_products} products, {total_images} optimised photos. "
        f"Manifest: {OUT / 'products.json'}",
        flush=True,
    )
    if total_images == 0:
        print("No product images were downloaded; refusing to publish an empty photo catalogue.", flush=True)
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.", file=sys.stderr)
        raise SystemExit(130)
