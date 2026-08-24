import requests
import time
from typing import Dict, List, Any, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class WikimediaAPIClient:
    """Client for interacting with Wikimedia Commons API with retry logic."""

    BASE_URL = "https://commons.wikimedia.org/w/api.php"
    DEFAULT_USER_AGENT = "WikimediaScraperBot/1.0"

    def __init__(self, max_retries: int = 3, timeout: int = 10):
        """
        Initialize the API client with retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": self.DEFAULT_USER_AGENT})

        return session

    def search_images(
        self,
        keyword: str,
        limit: int = 5,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for images on Wikimedia Commons.
        
        Args:
            keyword: Search term
            limit: Number of results per page (max 5 per spec)
            offset: Number of results to skip for pagination
            
        Returns:
            Dictionary containing search results and continuation token
        """
        params = {
            "action": "query",
            "list": "allimages",
            "aisort": "timestamp",
            "aidir": "descending",
            "aiprop": "url|user|timestamp",
            "ailimit": min(limit, 5),
            "aifrom": self._calculate_start_token(keyword, offset),
            "format": "json"
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "query": {}}

    def search_by_keyword(
        self,
        keyword: str,
        limit: int = 5,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for images by keyword on Wikimedia Commons.
        
        Args:
            keyword: Search term
            limit: Number of results per page
            offset: Pagination offset
            
        Returns:
            Dictionary containing search results
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"filetype:bitmap|drawing {keyword}",
            "srnamespace": "6",
            "srlimit": min(limit, 5),
            "sroffset": offset,
            "format": "json"
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "query": {}}

    def get_file_info(self, filenames: List[str]) -> Dict[str, Any]:
        """
        Get detailed information about specific files.
        
        Args:
            filenames: List of file names to query
            
        Returns:
            Dictionary containing file information
        """
        params = {
            "action": "query",
            "titles": "|".join(filenames),
            "prop": "imageinfo|pageterms",
            "iiprop": "url|user|timestamp|extmetadata",
            "format": "json"
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "query": {}}

    @staticmethod
    def _calculate_start_token(keyword: str, offset: int) -> str:
        """
        Calculate the starting point for pagination.
        
        Args:
            keyword: Search keyword
            offset: Pagination offset
            
        Returns:
            Start token for API query
        """
        if offset == 0:
            return ""
        return f"{keyword}_{offset}"
