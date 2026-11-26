import unittest
from pathlib import Path
from extract import extract, csv_cell


class ExtractionTests(unittest.TestCase):
    def test_fixture(self):
        row, = extract((Path(__file__).parent / "fixtures/yelp-search.html").read_text())
        self.assertEqual(row["review_count"], 21)
        self.assertEqual(row["categories"], "Coffee, Bakery")
        self.assertEqual(row["url"], "https://www.yelp.com/biz/synthetic-demo-coffee")

    def test_no_supported_data(self):
        self.assertEqual(extract("<title>Verification required</title>"), [])

    def test_ignores_non_yelp_urls(self):
        self.assertEqual(extract('<script type="application/ld+json">{"@type":"ItemList","itemListElement":[{"name":"Demo","url":"https://example.org/biz/demo"}]}</script>'), [])

    def test_spreadsheet_text(self):
        self.assertEqual(csv_cell(" =1+1"), "' =1+1")
