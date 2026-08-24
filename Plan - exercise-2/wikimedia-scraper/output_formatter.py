from typing import Dict, List, Any, Optional
from datetime import datetime


class OutputFormatter:
    """Formats search results as pretty-printed text."""

    @staticmethod
    def format_results(
        keyword: str,
        offset: int,
        batch_size: int,
        images: List[Dict[str, Any]],
        search_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format search results as pretty-printed text.
        
        Args:
            keyword: Search keyword used
            offset: Pagination offset
            batch_size: Batch size (5 per spec)
            images: List of image dictionaries with metadata
            search_info: Optional metadata about the search
            
        Returns:
            Formatted string with search results
        """
        lines = []
        lines.append("=" * 50)
        lines.append("Wikimedia Commons Image Metadata Results")
        lines.append("=" * 50)
        lines.append("")

        lines.append(f"Keyword: {keyword}")
        lines.append(f"Offset: {offset}")
        lines.append(f"Batch Size: {batch_size} images per page")
        lines.append(f"Results Fetched: {len(images)}")

        if search_info:
            lines.append(f"Query Time: {search_info.get('query_time', 'N/A')}")

        lines.append("-" * 50)
        lines.append("")

        if not images:
            lines.append("No images found for the given search criteria.")
            lines.append("")
        else:
            for index, image in enumerate(images, start=1):
                lines.append(OutputFormatter._format_image(index, image))

        lines.append("=" * 50)
        return "\n".join(lines)

    @staticmethod
    def _format_image(index: int, image: Dict[str, Any]) -> str:
        """
        Format a single image entry.
        
        Args:
            index: Image number in the result set
            image: Image metadata dictionary
            
        Returns:
            Formatted string for the image
        """
        title = image.get("title", "Unknown")
        url = image.get("url", "N/A")
        uploader = image.get("uploader", "Unknown")
        timestamp = image.get("timestamp", "N/A")
        description = image.get("description", "")

        lines = []
        lines.append(f"[{index}] Title: {title}")
        lines.append(f"    URL: {url}")
        lines.append(f"    Uploader: {uploader}")
        lines.append(f"    Date: {OutputFormatter._format_timestamp(timestamp)}")

        if description:
            lines.append(f"    Description: {description[:100]}...")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _format_timestamp(timestamp: str) -> str:
        """
        Format timestamp to human-readable format.
        
        Args:
            timestamp: Timestamp string (ISO format)
            
        Returns:
            Formatted timestamp string
        """
        if not timestamp or timestamp == "N/A":
            return "Unknown"

        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return timestamp

    @staticmethod
    def write_to_file(content: str, filepath: str) -> None:
        """
        Write formatted content to a file.
        
        Args:
            content: Formatted content string
            filepath: Path to output file
        """
        with open(filepath, "w") as f:
            f.write(content)

    @staticmethod
    def format_error(error_message: str, keyword: str = "") -> str:
        """
        Format an error message.
        
        Args:
            error_message: Error message text
            keyword: Search keyword (optional)
            
        Returns:
            Formatted error message
        """
        lines = []
        lines.append("=" * 50)
        lines.append("Error Occurred")
        lines.append("=" * 50)
        lines.append("")

        if keyword:
            lines.append(f"Keyword: {keyword}")

        lines.append(f"Error: {error_message}")
        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)
