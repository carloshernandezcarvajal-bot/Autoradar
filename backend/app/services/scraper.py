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
                        try:
                            await asyncio.wait_for(page.goto(url, wait_until="domcontentloaded"), timeout=25.0)
                        except Exception as e:
                            print(f"CarroYaScraper: Timeout en goto pagina {page_num}: {e}")
                            continue

                        try:
                            await asyncio.wait_for(page.wait_for_selector(".cy-publication-card-portal-ds-milla", state="attached"), timeout=15.0)
                        except Exception as e:
                            print(f"CarroYaScraper: Timeout en wait_for_selector pagina {page_num}: {e}")
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


class VendeTuNaveScraper(BaseScraper):
    BASE_URL = "https://www.vendetunave.co"

    async def scrape(self, max_pages: int = 5) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            page = await self.context.new_page()
            try:
                for page_num in range(1, max_pages + 1):
                    url = f"{self.BASE_URL}/vehiculos?page={page_num}"
                    try:
                        print(f"VendeTuNaveScraper: Procesando pagina {page_num}/{max_pages}...")
                        try:
                            await asyncio.wait_for(page.goto(url, wait_until="domcontentloaded"), timeout=25.0)
                        except Exception as e:
                            print(f"VendeTuNaveScraper: Timeout en goto pagina {page_num}: {e}")
                            continue

                        try:
                            await asyncio.wait_for(page.wait_for_selector("a[href*='/vehiculos/carrosycamionetas/']", state="attached"), timeout=15.0)
                        except Exception as e:
                            print(f"VendeTuNaveScraper: Timeout en wait_for_selector pagina {page_num}: {e}")
                            continue

                        await page.evaluate("window.scrollTo(0, 1000)")
                        await page.wait_for_timeout(1000)

                        cards = await page.query_selector_all("a[href*='/vehiculos/carrosycamionetas/']")
                        for card in cards:
                            try:
                                href = await card.get_attribute("href")
                                text = await card.inner_text()
                                if not href or not text:
                                    continue
                                
                                lines = [line.strip() for line in text.split("\n") if line.strip()]
                                if len(lines) < 2:
                                    continue
                                    
                                title = lines[0]
                                price_text = lines[1]
                                details = lines[2:]
                                
                                vehicle_data = self._parse_card(title, price_text, details, href)
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
        
        flat_details = []
        for d in details:
            if "-" in d:
                flat_details.extend(d.split("-"))
            elif "|" in d:
                flat_details.extend(d.split("|"))
            else:
                flat_details.append(d)
                
        flat_details = [f.strip() for f in flat_details if f.strip()]
        
        for detail in flat_details:
            if y := extract_year(detail):
                year = y
            if m := extract_mileage(detail):
                mileage = m

        if not year:
            match_title = re.search(r'\b(19\d{2}|20\d{2})\b', title)
            if match_title:
                year = int(match_title.group(1))

        if not year:
            return None

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            if str(year) in model_str:
                model_str = model_str.replace(str(year), "").strip()
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(title)
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link and link.startswith("/") else link
        if full_url:
            full_url = full_url.split("#")[0].split("?")[0]

        source_id = None
        if full_url:
            match_id = re.search(r'-(\d+)$', full_url)
            if match_id:
                source_id = match_id.group(1)

        return {
            "source": "vendetunave",
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


class SegundazoScraper(BaseScraper):
    BASE_URL = "https://www.segundazo.com.co"

    async def scrape(self, max_pages: int = 1) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            page = await self.context.new_page()
            try:
                url = f"{self.BASE_URL}/carros-usados/"
                print("SegundazoScraper: Procesando pagina...")
                try:
                    await asyncio.wait_for(page.goto(url, wait_until="domcontentloaded"), timeout=25.0)
                except Exception as e:
                    print(f"SegundazoScraper: Timeout en goto: {e}")
                    return vehicles

                try:
                    await asyncio.wait_for(page.wait_for_selector("article.card", state="attached"), timeout=15.0)
                except Exception as e:
                    print(f"SegundazoScraper: Timeout en wait_for_selector: {e}")
                    return vehicles

                cards = await page.query_selector_all("article.card")
                for card in cards:
                    try:
                        url_attr = await card.get_attribute("data-url")
                        title_el = await card.query_selector("h4")
                        small_el = await card.query_selector("small")
                        price_el = await card.query_selector(".price-main")
                        img_el = await card.query_selector("img")
                        
                        title = await title_el.inner_text() if title_el else ""
                        details_text = await small_el.inner_text() if small_el else ""
                        price_text = await price_el.inner_text() if price_el else ""
                        image_url = await img_el.get_attribute("src") if img_el else None
                        
                        if not title or not price_text:
                            continue
                            
                        details = [d.strip() for d in details_text.split("-") if d.strip()]
                        
                        vehicle_data = self._parse_card(title, price_text, details, url_attr, image_url)
                        if vehicle_data:
                            vehicles.append(vehicle_data)
                    except Exception:
                        continue
            finally:
                await page.close()
        finally:
            await self.close()
        return vehicles

    def _parse_card(self, title: str, price_text: str, details: list, link: str | None, image_url: str | None) -> dict | None:
        if not title:
            return None

        price = extract_price(price_text)
        if not price or price < 1000000:
            return None

        year = None
        mileage = None
        city = None
        
        for detail in details:
            if y := extract_year(detail):
                year = y
            elif m := extract_mileage(detail):
                mileage = m
            else:
                city = detail.strip().title()

        if not year:
            match_title = re.search(r'\b(19\d{2}|20\d{2})\b', title)
            if match_title:
                year = int(match_title.group(1))

        if not year:
            return None

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            if str(year) in model_str:
                model_str = model_str.replace(str(year), "").strip()
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(title)
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link and link.startswith("/") else link
        if full_url:
            full_url = full_url.split("#")[0].split("?")[0]

        source_id = None
        if full_url:
            source_id = full_url.split("/")[-2] if full_url.endswith("/") else full_url.split("/")[-1]

        return {
            "source": "segundazo",
            "source_id": source_id,
            "source_url": full_url or self.BASE_URL,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "currency": "COP",
            "title": title.strip(),
            "image_url": image_url,
            "city": city,
            "date_found": datetime.now(timezone.utc),
        }


class ListoYaAutosScraper(BaseScraper):
    BASE_URL = "https://listoyaautos.com"

    async def scrape(self, max_pages: int = 5) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            page = await self.context.new_page()
            try:
                for page_num in range(1, max_pages + 1):
                    url = f"{self.BASE_URL}/listings/page/{page_num}/"
                    try:
                        print(f"ListoYaAutosScraper: Procesando pagina {page_num}/{max_pages}...")
                        try:
                            await asyncio.wait_for(page.goto(url, wait_until="domcontentloaded"), timeout=25.0)
                        except Exception as e:
                            print(f"ListoYaAutosScraper: Timeout en goto pagina {page_num}: {e}")
                            break

                        try:
                            await asyncio.wait_for(page.wait_for_selector("div.listing-list-loop", state="attached"), timeout=15.0)
                        except Exception as e:
                            print(f"ListoYaAutosScraper: Timeout en wait_for_selector pagina {page_num}: {e}")
                            break

                        cards = await page.query_selector_all("div.listing-list-loop")
                        for card in cards:
                            try:
                                price_val = await card.get_attribute("data-price")
                                mileage_val = await card.get_attribute("data-mileage")
                                year_val = await card.get_attribute("data-numeric-ca-year")
                                
                                link_el = await card.query_selector("a[href*='/listings/']")
                                if not link_el:
                                    continue
                                    
                                href = await link_el.get_attribute("href")
                                title_el = await card.query_selector(".title, h3, h4")
                                if title_el:
                                    title = await title_el.inner_text()
                                else:
                                    title = await link_el.inner_text()
                                    
                                if not title:
                                    continue
                                title = re.sub(r'^\d+\s+m[áa]s\s+fotos\s+', '', title, flags=re.IGNORECASE).strip()
                                title = re.sub(r'^DESTACADO\s+', '', title, flags=re.IGNORECASE).strip()
                                
                                img_el = await card.query_selector("img")
                                image_url = await img_el.get_attribute("src") if img_el else None
                                
                                if not href or not title or not price_val:
                                    continue
                                    
                                city_el = await card.query_selector(".stm-car-city, [class*='city'], .location")
                                city = await city_el.inner_text() if city_el else None
                                
                                price = float(price_val)
                                year = int(year_val) if year_val else None
                                mileage = int(mileage_val) if mileage_val else None
                                
                                vehicle_data = self._parse_card(title, price, year, mileage, href, image_url, city)
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

    def _parse_card(self, title: str, price: float, year: int | None, mileage: int | None, link: str, image_url: str | None, city: str | None) -> dict | None:
        if not title or price < 1000000:
            return None

        if not year:
            match_title = re.search(r'\b(19\d{2}|20\d{2})\b', title)
            if match_title:
                year = int(match_title.group(1))

        if not year:
            return None

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            if str(year) in model_str:
                model_str = model_str.replace(str(year), "").strip()
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(parts[0])
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link.startswith("/") else link
        if full_url:
            full_url = full_url.split("#")[0].split("?")[0]

        source_id = None
        if full_url:
            source_id = full_url.split("/")[-2] if full_url.endswith("/") else full_url.split("/")[-1]

        return {
            "source": "listoya",
            "source_id": source_id,
            "source_url": full_url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "currency": "COP",
            "title": title.strip(),
            "image_url": image_url,
            "city": city.strip().title() if city else None,
            "date_found": datetime.now(timezone.utc),
        }


class CarMaxScraper(BaseScraper):
    BASE_URL = "https://www.carmaxcolombia.com.co"

    async def scrape(self, max_pages: int = 5) -> list[dict]:
        await self.start()
        vehicles = []
        try:
            page = await self.context.new_page()
            try:
                for page_num in range(1, max_pages + 1):
                    url = f"{self.BASE_URL}/cars_status/disponible/page/{page_num}/"
                    try:
                        print(f"CarMaxScraper: Procesando pagina {page_num}/{max_pages}...")
                        try:
                            await asyncio.wait_for(page.goto(url, wait_until="domcontentloaded"), timeout=25.0)
                        except Exception as e:
                            print(f"CarMaxScraper: Timeout en goto pagina {page_num}: {e}")
                            break

                        try:
                            await asyncio.wait_for(page.wait_for_selector("h5.sc_cars_item_title", state="attached"), timeout=15.0)
                        except Exception as e:
                            print(f"CarMaxScraper: Timeout en wait_for_selector pagina {page_num}: {e}")
                            break

                        h5_elements = await page.query_selector_all("h5.sc_cars_item_title")
                        for h5 in h5_elements:
                            try:
                                title = await h5.inner_text()
                                link_el = await h5.query_selector("a")
                                if not link_el:
                                    continue
                                    
                                href = await link_el.get_attribute("href")
                                if not href or not title:
                                    continue

                                card_data = await page.evaluate("""(h5) => {
                                    let card = h5;
                                    for (let j = 0; j < 5; j++) {
                                        if (card.parentElement) {
                                            card = card.parentElement;
                                            if (card.innerHTML.includes('$') || card.classList.contains('sc_cars_item')) {
                                                break;
                                            }
                                        }
                                    }
                                    
                                    let texts = [];
                                    card.querySelectorAll('div, p, span, li').forEach(el => {
                                        let t = el.innerText ? el.innerText.trim() : '';
                                        if (t && t.length < 150 && !texts.includes(t)) {
                                            texts.push(t);
                                        }
                                    });
                                    
                                    let img = card.querySelector('img');
                                    let img_url = img ? img.getAttribute('src') : '';
                                    
                                    return {
                                        texts: texts,
                                        image_url: img_url
                                    };
                                }""", h5)

                                texts = card_data.get("texts", [])
                                image_url = card_data.get("image_url")
                                
                                price = None
                                year = None
                                mileage = None
                                transmission = None
                                fuel_type = None
                                
                                for txt in texts:
                                    if '$' in txt or ',' in txt:
                                        p_val = extract_price(txt)
                                        if p_val and p_val >= 1000000:
                                            price = p_val
                                            
                                    if y_val := extract_year(txt):
                                        year = y_val
                                        
                                    if m_val := extract_mileage(txt):
                                        mileage = m_val
                                        
                                    if "autom" in txt.lower():
                                        transmission = "Automática"
                                    elif "mec" in txt.lower():
                                        transmission = "Mecánica"
                                        
                                    if "gasolina" in txt.lower():
                                        fuel_type = "Gasolina"
                                    elif "diesel" in txt.lower() or "díesel" in txt.lower():
                                        fuel_type = "Diésel"
                                    elif "hibr" in txt.lower() or "hybr" in txt.lower():
                                        fuel_type = "Híbrido"

                                if not price:
                                    for txt in texts:
                                        cleaned = txt.replace(",", "").replace(".", "").strip()
                                        if cleaned.isdigit() and len(cleaned) >= 7 and len(cleaned) <= 9:
                                            price = float(cleaned)
                                            break

                                vehicle_data = self._parse_card(title, price, year, mileage, href, image_url, transmission, fuel_type)
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

    def _parse_card(self, title: str, price: float | None, year: int | None, mileage: int | None, link: str, image_url: str | None, transmission: str | None, fuel_type: str | None) -> dict | None:
        if not title or not price or price < 1000000:
            return None

        if not year:
            match_title = re.search(r'\b(19\d{2}|20\d{2})\b', title)
            if match_title:
                year = int(match_title.group(1))

        if not year:
            return None

        parts = title.strip().split()
        if len(parts) >= 2:
            brand = normalize_brand(parts[0])
            model_str = " ".join(parts[1:])
            if str(year) in model_str:
                model_str = model_str.replace(str(year), "").strip()
            model = normalize_model(brand, model_str)
        else:
            brand = normalize_brand(parts[0])
            model = title.strip()

        full_url = f"{self.BASE_URL}{link}" if link.startswith("/") else link
        if full_url:
            full_url = full_url.split("#")[0].split("?")[0]

        source_id = None
        if full_url:
            source_id = full_url.split("/")[-2] if full_url.endswith("/") else full_url.split("/")[-1]

        return {
            "source": "carmax",
            "source_id": source_id,
            "source_url": full_url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "currency": "COP",
            "title": title.strip(),
            "image_url": image_url,
            "transmission": transmission,
            "fuel_type": fuel_type,
            "city": "Bogotá",
            "date_found": datetime.now(timezone.utc),
        }

