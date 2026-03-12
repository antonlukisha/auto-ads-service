import time
from multiprocessing import Process
from typing import cast

from sqlalchemy import BinaryExpression, create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import get_config
from app.core.logging import get_logger
from app.models.sqlalchemy_models import Car
from app.scraper.parser import CarsNetScraper

logger = get_logger("scraper.worker")


class ScraperWorker:
    def __init__(self, interval_hours: int = 3, max_pages: int = 3) -> None:
        self.interval_hours = interval_hours
        self.max_pages = max_pages
        self.process: Process | None = None
        self.running = False

    @staticmethod
    def _save_cars_to_db(cars: list[dict]) -> tuple[int, int]:
        """
        Save cars to database

        :param cars: List of car data dictionaries
        :type cars: list[dict]
        :return: Tuple of new and updated counts
        :return type: tuple[int, int]
        """
        cfg = get_config()
        engine = create_engine(cfg.postgres_dsn.replace("+asyncpg", ""))
        Session = sessionmaker(bind=engine)
        session = Session()

        new_count = 0
        updated_count = 0

        try:
            for car_data in cars:
                existing = session.execute(
                    select(Car).where(cast(BinaryExpression, Car.url == car_data["url"]))
                ).scalar_one_or_none()

                if existing:
                    for key, value in car_data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                else:
                    car = Car(**car_data)
                    session.add(car)
                    new_count += 1

            session.commit()

        except Exception as e:
            logger.error(f"Failed to save cars to database: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            engine.dispose()

        return new_count, updated_count

    def _run_cycle(self, scraper: CarsNetScraper) -> None:
        """
        Run a single scraping cycle

        :param scraper: Scraper instance
        :type scraper: CarsNetScraper
        :return: nothing
        :rtype: None
        """
        logger.debug("Starting scraping...")

        cars = scraper.scrape_all_pages(max_pages=self.max_pages)

        if cars:
            new, updated = self._save_cars_to_db(cars)
            logger.debug(f"Saved: {new} new, {updated} updated")

    def _worker_loop(self) -> None:
        """
        Worker loop
        """
        scraper = CarsNetScraper()

        scraper.update_rate()

        cycle_count = 0

        while self.running:
            cycle_count += 1
            try:

                self._run_cycle(scraper)

                if cycle_count % 24 == 0:
                    scraper.update_rate()

                sleep_seconds = self.interval_hours * 3600

                for _ in range(sleep_seconds // 10):
                    if not self.running:
                        break
                    time.sleep(10)
            except KeyboardInterrupt:
                logger.debug("Worker received shutdown signal")
                break
            except Exception as e:
                logger.error(f"Error in scraping cycle: {e}", exc_info=True)
                logger.debug("Waiting 5 minutes before retry...")
                for _ in range(300 // 10):
                    if not self.running:
                        break
                    time.sleep(10)

        logger.debug("Scraper worker stopped")

    def start(self) -> None:
        """
        Start the worker
        """
        if self.process and self.process.is_alive():
            logger.warning("Worker already running")
            return

        self.running = True
        self.process = Process(target=self._worker_loop, daemon=True, name="scraper_worker")
        self.process.start()
        logger.info(f"Scraper worker started with PID: {self.process.pid}")

    def stop(self) -> None:
        """
        Stop the worker
        """
        self.running = False

        if self.process and self.process.is_alive():
            logger.info("Stopping scraper worker...")
            self.process.terminate()
            self.process.join(timeout=5)

            if self.process.is_alive():
                logger.warning("Worker did not terminate, killing...")
                self.process.kill()

            logger.info("Scraper worker stopped")

    @property
    def is_running(self) -> bool:
        """
        Check if the worker is running

        :return: True if running, False otherwise
        :rtype: bool
        """
        return self.process is not None and self.process.is_alive()


scraper_worker = ScraperWorker(interval_hours=3, max_pages=3)
