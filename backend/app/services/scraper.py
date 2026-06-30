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
        self.context = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

    async def close(self):
        if self.context:
            await self.context.close()
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
            page = await self.context.new_page()
            try:
                for page_num in range(1, max_pages + 1):
                    url = f"{self.BASE_URL}/vehiculos/_NoIndex_True_Desde_{page_num * 48}_OrderId_PRICE"
                    try:
                        print(f"TuCarroScraper: Procesando pagina {page_num}/{max_pages}...")
                        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                        await page.wait_for_timeout(2000)

                        cards = await page.query_selector_all(".poly-card")
                        for card in cards:
                            try:
                                link_el = await card.query_selector("a.poly-component__title")
                                link = await link_el.get_attribute("href") if link_el else ""
                                title = await link_el.inner_text() if link_el else ""

                                price_el = await card.query_selector(".andes-money-amount__fraction")
                                price_text = await price_el.inner_text() if price_el else ""

                                attrs = await card.query_selector_all(".poly-attributes-list__item")
                                details = [await a.inner_text() for a in attrs]

                                vehicle_data = self._parse_card(title, price_text, details, link)
                                if vehicle_data:
                                    vehicles.append(vehicle_data)
                            except Exception:
                                continue
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
        if not price or price < 1000000:
            return None

        year = None
        mileage = None
        for detail in details:
            if y := extract_year(detail):
                year = y
            if m := extract_mileage(detail):
                mileage = m

        # Deducir año de la URL o del titulo si no esta en detalles
        if not year and link:
            match = re.search(r'-(\d{4})-_', link)
            if match:
                year = int(match.group(1))
            else:
                match_title = re.search(r'\b(19\d{2}|20\d{2})\b', title)
                if match_title:
                    year = int(match_title.group(1))

        # Si no tiene año, descartar para evitar datos corruptos
        if not year:
            return None

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(title)
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link and link.startswith("/") else link
        if full_url:
            full_url = full_url.split("#")[0].split("?")[0]

        source_id = None
        if full_url:
            match_id = re.search(r'(MCO-\d+)', full_url)
            if match_id:
                source_id = match_id.group(1)

        return {
            "source": "tucarro",
            "source_id": source_id,
            "source_url": full_url or self.BASE_URL,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "currency": "COP",
            "title": title.strip(),
            "date_found": datetime.now(timezone.utc),
        }


class CarroYaScraper(BaseScraper):
    BASE_URL = "https://carroya.com"

    async def scrape(self, max_pages: int = 5) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            page = await self.context.new_page()
            try:
                for page_num in range(1, max_pages + 1):
                    url = f"{self.BASE_URL}/carros-usados/pagina-{page_num}"
                    try:
                        print(f"CarroYaScraper: Procesando pagina {page_num}/{max_pages}...")
                        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                        try:
                            await page.wait_for_selector(".cy-publication-card-portal-ds-milla", timeout=15000)
                        except Exception:
                            continue

                        # Realizar scroll vertical progresivo para activar el lazy loading de las tarjetas principales
                        for i in range(5):
                            await page.evaluate(f"window.scrollTo(0, {i * 1000})")
                            await page.wait_for_timeout(500)

                        items = await page.query_selector_all(".cy-publication-card-portal-ds-milla")
                        for item in items:
                            try:
                                title_el = await item.query_selector("h3, h2")
                                title = await title_el.inner_text() if title_el else ""

                                price_el = await item.query_selector("h4.price, [class*='price']")
                                price_text = await price_el.inner_text() if price_el else ""

                                detail_els = await item.query_selector_all("[class*='publication-detail-tag'], [class*='detail']")
                                details = [await d.inner_text() for d in detail_els]

                                link_el = await item.query_selector("a[class*='publication-basic-data'], a")
                                link = await link_el.get_attribute("href") if link_el else None

                                vehicle_data = self._parse_card(title, price_text, details, link)
                                if vehicle_data:
                                    vehicles.append(vehicle_data)
                            except Exception:
                                continue
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
        if not price or price < 1000000:
            return None

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
        if full_url:
            full_url = full_url.split("#")[0].split("?")[0]

        source_id = None
        if full_url:
            match_id = re.search(r'/(\d+)$', full_url)
            if match_id:
                source_id = match_id.group(1)

        return {
            "source": "carroya",
            "source_id": source_id,
            "source_url": full_url or self.BASE_URL,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "currency": "COP",
            "title": title.strip(),
            "date_found": datetime.now(timezone.utc),
        }
