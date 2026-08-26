import unittest
from unittest.mock import Mock

import requests

from wikimedia_api_client import WikimediaAPIClient


class TestWikimediaAPIClient(unittest.TestCase):
    def _client_with_response(self, response):
        client = WikimediaAPIClient.__new__(WikimediaAPIClient)
        client.timeout = 10
        client.session = Mock()
        client.session.get.return_value = response
        return client

    def test_search_by_keyword_forwards_offset_and_caps_batch_size(self):
        response = Mock()
        response.json.return_value = {"query": {"search": []}}
        client = self._client_with_response(response)

        client.search_by_keyword("butterfly", limit=10, offset=10)

        request = client.session.get.call_args
        self.assertEqual(request.kwargs["params"]["srsearch"], "filetype:bitmap|drawing butterfly")
        self.assertEqual(request.kwargs["params"]["sroffset"], 10)
        self.assertEqual(request.kwargs["params"]["srlimit"], 5)

    def test_search_by_keyword_returns_api_error(self):
        client = self._client_with_response(requests.exceptions.Timeout("timed out"))
        client.session.get.side_effect = requests.exceptions.Timeout("timed out")

        result = client.search_by_keyword("butterfly", offset=5)

        self.assertIn("error", result)
        self.assertEqual(result["query"], {})


if __name__ == "__main__":
    unittest.main()
