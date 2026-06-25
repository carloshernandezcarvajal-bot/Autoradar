import asyncio
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.services.normalization import (
    normalize_brand,
    normalize_model,
    extract_year,
    extract_mileage,
    extract_price,
)


class BaseScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape(self) -> list[dict]:
        raise NotImplementedError


class TuCarroScraper(BaseScraper):
    BASE_URL = "https://www.tucarro.com.co"

    async def scrape(self, max_pages: int = 5) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            for page_num in range(1, max_pages + 1):
                url = f"{self.BASE_URL}/vehiculos/_NoIndex_True_Desde_{page_num * 48}_OrderId_PRICE"
                page = await self.browser.new_page()
                try:
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    cards = await page.query_selector_all('a[href*="/MCO-"]')
                    for card in cards:
                        try:
                            link = await card.get_attribute("href")
                            title_el = await card.query_selector("h2")
                            title = await title_el.inner_text() if title_el else ""

                            price_el = await card.query_selector("[class*='price']")
                            price_text = await price_el.inner_text() if price_el else ""

                            attrs = await card.query_selector_all("[class*='attributes'] span")
                            details = [await a.inner_text() for a in attrs]

                            vehicle_data = self._parse_card(title, price_text, details, link)
                            if vehicle_data:
                                vehicles.append(vehicle_data)
                        except Exception:
                            continue
                finally:
                    await page.close()
        finally:
            await self.close()
        return vehicles

    def _parse_card(self, title: str, price_text: str, details: list, link: str | None) -> dict | None:
        if not title:
            return None

        price = extract_price(price_text)
        year = None
        mileage = None
        for detail in details:
            if y := extract_year(detail):
                year = y
            if m := extract_mileage(detail):
                mileage = m

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(title)
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link and link.startswith("/") else link

        return {
            "source": "tucarro",
            "source_url": full_url or self.BASE_URL,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price or 0,
            "currency": "COP",
            "title": title.strip(),
            "date_found": datetime.now(timezone.utc).isoformat(),
        }


class CarroYaScraper(BaseScraper):
    BASE_URL = "https://carroya.com"

    async def scrape(self, max_pages: int = 5) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            for page_num in range(1, max_pages + 1):
                url = f"{self.BASE_URL}/carros-usados?pagina={page_num}"
                page = await self.browser.new_page()
                try:
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    items = await page.query_selector_all("[class*='listing'], [class*='card'], [class*='item']")
                    for item in items:
                        try:
                            title_el = await item.query_selector("h2, h3, [class*='title'], [class*='name']")
                            title = await title_el.inner_text() if title_el else ""

                            price_el = await item.query_selector("[class*='price']")
                            price_text = await price_el.inner_text() if price_el else ""

                            detail_els = await item.query_selector_all("[class*='detail'], [class*='spec'], span")
                            details = [await d.inner_text() for d in detail_els]

                            link_el = await item.query_selector("a")
                            link = await link_el.get_attribute("href") if link_el else None

                            vehicle_data = self._parse_card(title, price_text, details, link)
                            if vehicle_data:
                                vehicles.append(vehicle_data)
                        except Exception:
                            continue
                finally:
                    await page.close()
        finally:
            await self.close()
        return vehicles

    def _parse_card(self, title: str, price_text: str, details: list, link: str | None) -> dict | None:
        if not title:
            return None

        price = extract_price(price_text)
        year = None
        mileage = None
        for detail in details:
            if y := extract_year(detail):
                year = y
            if m := extract_mileage(detail):
                mileage = m

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(title)
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link and link.startswith("/") else link

        return {
            "source": "carroya",
            "source_url": full_url or self.BASE_URL,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price or 0,
            "currency": "COP",
            "title": title.strip(),
            "date_found": datetime.now(timezone.utc).isoformat(),
        }
