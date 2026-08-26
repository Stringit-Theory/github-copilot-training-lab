#!/usr/bin/env python3
"""
Wikimedia Commons Image Metadata Scraper

Scrapes image metadata from Wikimedia Commons for a given keyword,
with pagination support and a batch size of 5 images per page.

Usage:
    python wikimedia_scraper.py config.yaml
"""

import argparse
import json
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from config_validator import ConfigValidator
from wikimedia_api_client import WikimediaAPIClient
from output_formatter import OutputFormatter


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WikimediaScraper:
    """Main scraper orchestrator."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scraper with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.api_client = WikimediaAPIClient(
            max_retries=config['max_retries'],
            timeout=config['request_timeout']
        )

    def run(self) -> bool:
        """
        Execute the scraping operation.
        
        Returns:
            True if successful, False otherwise
        """
        keyword = self.config['keyword']
        offset = self.config['offset']
        batch_size = self.config['batch_size']
        output_file = self.config['output_file']
        metadata_output_dir = self.config['metadata_output_dir']

        logger.info(f"Starting search for keyword: '{keyword}'")
        logger.info(f"Offset: {offset}, Batch size: {batch_size}")

        try:
            images = self._fetch_images(keyword, batch_size, offset)

            if not images:
                logger.warning(f"No images found for keyword: '{keyword}'")

            self._save_recent_metadata(images, metadata_output_dir)

            # Format results
            formatted_output = OutputFormatter.format_results(
                keyword=keyword,
                offset=offset,
                batch_size=batch_size,
                images=images,
                search_info={"query_time": "N/A"}
            )

            # Output results
            if output_file:
                logger.info(f"Writing results to file: {output_file}")
                OutputFormatter.write_to_file(formatted_output, output_file)
                logger.info("Results written successfully")
            else:
                print(formatted_output)

            return True

        except Exception as e:
            error_msg = OutputFormatter.format_error(str(e), keyword)
            if output_file:
                OutputFormatter.write_to_file(error_msg, output_file)
            else:
                print(error_msg)

            logger.error(f"Scraping failed: {str(e)}")
            return False

    def _fetch_images(
        self,
        keyword: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch images from Wikimedia Commons.
        
        Args:
            keyword: Search keyword
            limit: Results per page
            offset: Pagination offset
            
        Returns:
            List of image metadata dictionaries
        """
        logger.info(f"Querying Wikimedia Commons API...")

        result = self.api_client.search_by_keyword(keyword, limit, offset)

        if "error" in result:
            raise Exception(f"API Error: {result['error']}")

        images = []
        query_data = result.get("query", {})

        if "search" in query_data:
            search_results = query_data["search"]
            logger.info(f"Found {len(search_results)} results")

            for search_item in search_results[:limit]:
                # Extract filename from title
                title = search_item.get("title", "")

                # Get detailed file information
                file_info = self.api_client.get_file_info([title])
                file_data = file_info.get("query", {}).get("pages", {})

                for page_id, page_info in file_data.items():
                    if page_id == "-1":
                        continue

                    imageinfo_list = page_info.get("imageinfo", [])
                    if not imageinfo_list:
                        continue

                    img_info = imageinfo_list[0]

                    image_data = {
                        "title": page_info.get("title", title),
                        "url": img_info.get("url", ""),
                        "uploader": img_info.get("user", "Unknown"),
                        "timestamp": img_info.get("timestamp", ""),
                        "description": self._extract_description(img_info),
                        "extmetadata": img_info.get("extmetadata", {})
                    }
                    images.append(image_data)

                    if len(images) >= limit:
                        break

        else:
            logger.warning("No search results in API response")

        return images[:limit]

    @staticmethod
    def _parse_timestamp(timestamp: str) -> Optional[datetime]:
        """Parse an API timestamp as a timezone-aware UTC datetime."""
        if not timestamp:
            return None

        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @classmethod
    def _select_recent_images(
        cls,
        images: List[Dict[str, Any]],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Return the newest images, with undated results as a fallback."""
        epoch = datetime.min.replace(tzinfo=timezone.utc)
        ranked_images = sorted(
            enumerate(images),
            key=lambda item: (
                cls._parse_timestamp(item[1].get("timestamp", "")) is not None,
                cls._parse_timestamp(item[1].get("timestamp", "")) or epoch,
                -item[0]
            ),
            reverse=True
        )
        return [image for _, image in ranked_images[:limit]]

    @staticmethod
    def _metadata_filename(title: str) -> str:
        """Create a safe sidecar filename from a Wikimedia file title."""
        image_name = title[5:] if title.startswith("File:") else title
        image_name = image_name.replace("\\", "/")
        image_name = Path(image_name).name
        stem = Path(image_name).stem or "image"
        return f"{stem}.txt"

    @staticmethod
    def _metadata_value(value: Any) -> str:
        """Serialize metadata values in a stable readable form."""
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        if isinstance(value, (list, tuple)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @classmethod
    def _format_attribution_metadata(cls, image: Dict[str, Any]) -> str:
        """Format one image's attribution metadata as text."""
        title = image.get("title", "Unknown")
        lines = [f"Attribution metadata for {title}"]

        for field in ("url", "uploader", "timestamp", "description"):
            value = image.get(field, "")
            if value:
                lines.append(f"{field}: {value}")

        extmetadata = image.get("extmetadata", {})
        if isinstance(extmetadata, dict):
            for key in sorted(extmetadata):
                lines.append(f"{key}: {cls._metadata_value(extmetadata[key])}")

        return "\n".join(lines) + "\n"

    @classmethod
    def _save_recent_metadata(
        cls,
        images: List[Dict[str, Any]],
        output_dir: str
    ) -> None:
        """Write sidecar attribution files for up to three recent images."""
        recent_images = cls._select_recent_images(images)
        if not recent_images:
            return

        metadata_dir = Path(output_dir)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        for image in recent_images:
            filename = cls._metadata_filename(image.get("title", "image"))
            OutputFormatter.write_to_file(
                cls._format_attribution_metadata(image),
                str(metadata_dir / filename)
            )

    @staticmethod
    def _extract_description(img_info: Dict[str, Any]) -> str:
        """
        Extract description from image metadata.
        
        Args:
            img_info: Image information dictionary
            
        Returns:
            Description string or empty string
        """
        extmetadata = img_info.get("extmetadata", {})

        # Try common metadata fields
        description_keys = ["ImageDescription", "Summary", "Description"]
        for key in description_keys:
            if key in extmetadata:
                value = extmetadata[key]
                if isinstance(value, dict):
                    return value.get("value", "")
                return str(value)

        return ""


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Scrape image metadata from Wikimedia Commons"
    )
    parser.add_argument(
        "config",
        help="Path to configuration file (YAML/JSON)"
    )

    args = parser.parse_args()

    # Load and validate configuration
    try:
        config = ConfigValidator.load_config(args.config)
        logger.info("Configuration loaded successfully")
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Configuration error: {str(e)}")
        return 1

    # Run scraper
    scraper = WikimediaScraper(config)
    success = scraper.run()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
