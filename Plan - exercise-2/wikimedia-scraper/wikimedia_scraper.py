#!/usr/bin/env python3
"""
Wikimedia Commons Image Metadata Scraper

Scrapes image metadata from Wikimedia Commons for a given keyword,
with pagination support and a batch size of 5 images per page.

Usage:
    python wikimedia_scraper.py config.yaml
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

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

        logger.info(f"Starting search for keyword: '{keyword}'")
        logger.info(f"Offset: {offset}, Batch size: {batch_size}")

        try:
            images = self._fetch_images(keyword, batch_size, offset)

            if not images:
                logger.warning(f"No images found for keyword: '{keyword}'")

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
                        "description": self._extract_description(img_info)
                    }
                    images.append(image_data)

                    if len(images) >= limit:
                        break

        else:
            logger.warning("No search results in API response")

        return images[:limit]

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
