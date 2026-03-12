import random
import re
import time
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.logging import get_logger

logger = get_logger("scraper.parser")


class CarsNetScraper:
    BASE_URL = "https://www.carsensor.net"
    LISTING_URL = f"{BASE_URL}/usedcar/"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        self.max_retries = 3
        self.request_timeout = 30
        self.translator_en = GoogleTranslator(source="ja", target="en")
        self.translator_ru = GoogleTranslator(source="ja", target="ru")
        self.jpy_to_rub = 0.498

    def _rotate_user_agent(self) -> None:
        """
        Rotate user agent
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]
        self.session.headers.update({"User-Agent": random.choice(user_agents)})

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            )
        ),
    )
    def _make_request(self, url: str, params: dict | None = None) -> requests.Response:
        """
        Make a request with retry logic

        :param url: URL to request
        :type url: str
        :param params: Request parameters
        :type params: dict | None
        :return: Response object
        :rtype: requests.Response
        """
        self._rotate_user_agent()

        response = self.session.get(
            url, params=params, timeout=self.request_timeout, allow_redirects=True
        )

        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 60))
            logger.warning(f"Rate limited. Waiting {wait_time} seconds")
            time.sleep(wait_time)
            response = self._make_request(url, params)

        response.encoding = "utf-8"
        response.raise_for_status()
        return response

    def parse_listing_page(self, html: str) -> list[dict[str, Any]]:
        """
        Parse listing page

        :param html: HTML content
        :type html: str
        :return: List of car details
        :rtype: list[dict[str, Any]]
        """
        soup = BeautifulSoup(html, "html.parser")
        cars = []
        listings = soup.select(".cassetteWrap.js-mainCassette")

        if not listings:
            return []

        for item in listings:
            try:
                brand_elem = item.select_one(".cassetteMain__carInfoContainer > p")
                brand_ja = brand_elem.text.strip() if brand_elem else ""
                brand = self.translator_en.translate(brand_ja) if brand_ja else ""

                title_elem = item.select_one(".cassetteMain__title a")
                title_text = title_elem.text.strip() if title_elem else ""
                model_ja = ""
                if brand_ja and title_text.startswith(brand_ja):
                    model_ja = title_text[len(brand_ja) :].strip().split(" ")[0]
                elif title_text:
                    model_ja = title_text.split(" ")[0]
                model = self.translator_en.translate(model_ja) if model_ja else ""

                year = 0
                for spec in item.select(".specList__detailBox"):
                    dt = spec.select_one(".specList__title")
                    if dt and "年式" in dt.text:
                        dd = spec.select_one(".specList__data")
                        if dd:
                            year_match = re.search(r"(\d{4})", dd.text.strip())
                            year = int(year_match.group(1)) if year_match else 0
                        break

                price = 0
                price_elem = item.select_one(".totalPrice__content") or item.select_one(
                    ".basePrice__content"
                )
                if price_elem:
                    price_digits = re.sub(r"[^\d.]", "", price_elem.text.strip())
                    if price_digits:
                        price = int(float(price_digits) * 10000)

                color_ja = "不明"
                color_item = item.select_one(".carBodyInfoList__item:last-child")
                if color_item:
                    color_ja = re.sub(r"[Ｍ◆]", "", color_item.text).strip()
                color = (
                    self.translator_ru.translate(color_ja) if color_ja != "不明" else "неизвестный"
                )

                link_elem = item.select_one(".cassetteMain__title a")
                url = (
                    urljoin(self.BASE_URL, str(link_elem["href"]))
                    if link_elem and link_elem.get("href")
                    else ""
                )

                if brand and model and year and price and url:
                    cars.append(
                        {
                            "brand": brand.title(),
                            "model": model.title(),
                            "year": year,
                            "price": price * self.jpy_to_rub,
                            "color": color,
                            "url": url,
                        }
                    )

            except Exception as e:
                logger.error(f"Error parsing item: {e}")
                continue

        return cars

    def scrape_page(self, page: int = 1) -> list[dict[str, Any]]:
        """
        Scrape a single page

        :param page: Page number
        :type page: int
        :return: List of car details
        :rtype: list[dict[str, Any]]
        """
        url = self.LISTING_URL if page == 1 else f"{self.LISTING_URL}index{page}.html?SORT=19"
        try:
            response = self._make_request(url)
            return self.parse_listing_page(response.text)
        except Exception as e:
            logger.error(f"Failed to scrape page {page}: {e}")
            return []

    def scrape_all_pages(self, max_pages: int = 3) -> list[dict[str, Any]]:
        """
        Scrape all pages

        :param max_pages: Maximum number of pages to scrape
        :type max_pages: int
        :return: List of car details
        :rtype: list[dict[str, Any]]
        """
        all_cars = []
        for page in range(1, max_pages + 1):
            cars = self.scrape_page(page)
            all_cars.extend(cars)
            if not cars:
                break
            time.sleep(random.uniform(2, 5))
        return all_cars

    def update_rate(self) -> None:
        """
        Update JPY to RUB exchange rate
        """
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/JPY")
            data = response.json()
            self.jpy_to_rub = data["rates"]["RUB"]
        finally:
            pass
