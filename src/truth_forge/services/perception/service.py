"""Perception Service.

The sensory organs of the organism.
"""

from __future__ import annotations

from typing import Any, cast

import requests
from bs4 import BeautifulSoup

from truth_forge.services.base import BaseService, MediatorProtocol
from truth_forge.services.factory import get_service, register_service


@register_service()
class PerceptionService(BaseService):
    """A service for perceiving the external world by scraping websites and polling APIs."""

    service_name = "perception"
    mediator: MediatorProtocol  # Type annotation for the mediator

    def on_startup(self) -> None:
        """Initialize the service."""
        self.mediator = cast("MediatorProtocol", get_service("mediator"))
        self.http_session = requests.Session()
        self.http_session.headers.update(
            {"User-Agent": "TruthForgeOrganism/1.0; (+https://truth-forge.ai/bot)"}
        )

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Processes a perception command received via inhale."""
        perception_type = record.get("type")
        source = record.get("source")

        if not all([perception_type, source]):
            raise ValueError("Perception command requires 'type' and 'source'.")

        # After validation, we know these are strings
        assert isinstance(source, str), "source must be a string"

        try:
            if perception_type == "scrape_website":
                self.scrape_website(source)
            elif perception_type == "poll_api":
                self.poll_api(source)
            else:
                self.logger.warning("unknown_perception_type", type=perception_type)
        except Exception as e:
            self.logger.error(
                "perception_failed", type=perception_type, source=source, error=str(e)
            )
            self._write_error_signal(record, e)

        return record

    def poll_api(self, url: str) -> None:
        """Polls a JSON API and publishes its content."""
        try:
            response = self.http_session.get(url, timeout=15)
            response.raise_for_status()
            api_data = response.json()

            data = {"source": url, "content": api_data, "content_type": "application/json"}
            self.mediator.publish("knowledge.process", data)
            self.logger.info("api_polled", url=url)
        except requests.RequestException as e:
            self.logger.error("api_poll_failed", url=url, error=str(e))
            raise

    def scrape_website(self, url: str) -> None:
        """Scrapes a website's main text content and publishes it."""
        try:
            response = self.http_session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Find the main content, fall back to body
            main_content = soup.find("main") or soup.find("body")

            text_content = main_content.get_text(separator="\n", strip=True) if main_content else ""

            data = {"source": url, "content": text_content, "content_type": "text/plain"}
            self.mediator.publish("knowledge.process", data)
            self.logger.info("website_scraped", url=url, content_length=len(text_content))
        except requests.RequestException as e:
            self.logger.error("website_scrape_failed", url=url, error=str(e))
            raise
