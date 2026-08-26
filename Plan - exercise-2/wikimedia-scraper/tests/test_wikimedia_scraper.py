import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

from wikimedia_scraper import WikimediaScraper


class TestWikimediaScraper(unittest.TestCase):
    def _scraper(self, metadata_output_dir="metadata"):
        scraper = WikimediaScraper.__new__(WikimediaScraper)
        scraper.config = {
            "keyword": "nature",
            "offset": 0,
            "batch_size": 5,
            "output_file": None,
            "metadata_output_dir": metadata_output_dir,
        }
        scraper.api_client = Mock()
        return scraper

    def test_fetch_images_retains_complete_extmetadata(self):
        scraper = self._scraper()
        scraper.api_client.search_by_keyword.return_value = {
            "query": {"search": [{"title": "File:fern.jpg"}]}
        }
        scraper.api_client.get_file_info.return_value = {
            "query": {"pages": {"1": {
                "title": "File:fern.jpg",
                "imageinfo": [{
                    "url": "https://example.test/fern.jpg",
                    "user": "Photographer",
                    "timestamp": "2026-01-02T03:04:05Z",
                    "extmetadata": {
                        "Artist": {"value": "Photographer"},
                        "License": {"value": "CC BY-SA"},
                    },
                }],
            }}}
        }

        images = scraper._fetch_images("nature", 5, 0)

        self.assertEqual(images[0]["extmetadata"]["Artist"]["value"], "Photographer")
        self.assertIn("License", images[0]["extmetadata"])

    def test_fetch_images_returns_at_most_five_results(self):
        scraper = self._scraper()
        scraper.api_client.search_by_keyword.return_value = {
            "query": {
                "search": [{"title": f"File:image-{index}.jpg"} for index in range(7)]
            }
        }
        scraper.api_client.get_file_info.side_effect = [
            {
                "query": {
                    "pages": {
                        str(index): {
                            "title": f"File:image-{index}.jpg",
                            "imageinfo": [{"url": f"https://example.test/{index}.jpg"}],
                        }
                    }
                }
            }
            for index in range(5)
        ]

        images = scraper._fetch_images("nature", limit=5, offset=10)

        self.assertEqual(len(images), 5)
        self.assertEqual(scraper.api_client.search_by_keyword.call_args.args, ("nature", 5, 10))
        self.assertEqual(scraper.api_client.get_file_info.call_count, 5)

    def test_fetch_images_raises_for_api_error(self):
        scraper = self._scraper()
        scraper.api_client.search_by_keyword.return_value = {
            "error": "request failed"
        }

        with self.assertRaisesRegex(Exception, "API Error: request failed"):
            scraper._fetch_images("nature", limit=5, offset=0)

    def test_select_recent_images_uses_timestamp_and_fallback_order(self):
        images = [
            {"title": "old", "timestamp": "2024-01-01T00:00:00Z"},
            {"title": "missing", "timestamp": ""},
            {"title": "newest", "timestamp": "2026-01-01T00:00:00Z"},
            {"title": "invalid", "timestamp": "not-a-date"},
            {"title": "middle", "timestamp": "2025-01-01T00:00:00Z"},
        ]

        selected = WikimediaScraper._select_recent_images(images)

        self.assertEqual(
            [image["title"] for image in selected],
            ["newest", "middle", "old"],
        )

    def test_select_recent_images_preserves_order_when_all_timestamps_invalid(self):
        images = [
            {"title": "first", "timestamp": "invalid"},
            {"title": "second", "timestamp": ""},
            {"title": "third", "timestamp": "also invalid"},
        ]

        selected = WikimediaScraper._select_recent_images(images)

        self.assertEqual([image["title"] for image in selected], ["first", "second", "third"])

    def test_metadata_filename_uses_image_stem_and_prevents_nested_paths(self):
        self.assertEqual(
            WikimediaScraper._metadata_filename("File:folder/Red Riding Hood.png"),
            "Red Riding Hood.txt",
        )
        self.assertEqual(
            WikimediaScraper._metadata_filename("File:portrait"),
            "portrait.txt",
        )

    def test_save_recent_metadata_writes_three_files_with_required_header(self):
        images = [
            {"title": "File:old.jpg", "timestamp": "2024-01-01T00:00:00Z",
             "url": "https://example.test/old.jpg",
             "extmetadata": {"Artist": {"value": "Older artist"}}},
            {"title": "File:newest.png", "timestamp": "2026-01-01T00:00:00Z",
             "url": "https://example.test/newest.png",
             "extmetadata": {"LicenseShortName": {"value": "CC BY-SA"}}},
            {"title": "File:middle.gif", "timestamp": "2025-01-01T00:00:00Z",
             "extmetadata": {}},
            {"title": "File:excluded.jpg", "timestamp": "2023-01-01T00:00:00Z",
             "extmetadata": {}},
        ]

        with tempfile.TemporaryDirectory() as temporary_dir:
            output_dir = Path(temporary_dir) / "nested" / "metadata"
            WikimediaScraper._save_recent_metadata(images, str(output_dir))

            self.assertEqual(
                sorted(path.name for path in output_dir.iterdir()),
                ["middle.txt", "newest.txt", "old.txt"],
            )
            content = (output_dir / "newest.txt").read_text(encoding="utf-8")
            self.assertTrue(content.startswith("Attribution metadata for File:newest.png\n"))
            self.assertIn("LicenseShortName: {\"value\": \"CC BY-SA\"}", content)
            self.assertFalse((output_dir / "excluded.txt").exists())

    def test_run_honors_configured_metadata_directory(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            output_dir = Path(temporary_dir) / "configured"
            scraper = self._scraper(str(output_dir))
            images = [{
                "title": "File:one.jpg",
                "timestamp": "2026-01-01T00:00:00Z",
                "url": "https://example.test/one.jpg",
                "extmetadata": {},
            }]
            with patch.object(scraper, "_fetch_images", return_value=images):
                with patch("builtins.print"):
                    self.assertTrue(scraper.run())

            self.assertTrue((output_dir / "one.txt").is_file())


if __name__ == "__main__":
    unittest.main()
