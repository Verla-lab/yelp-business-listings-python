import argparse
import csv
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

FIELDS = ("name", "categories", "rating", "review_count", "url")


class StructuredData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.blocks = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.active = dict(attrs).get("type") == "application/ld+json"
            self.parts = []

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.active:
            self.blocks.append("".join(self.parts))
            self.active = False


def nodes(value):
    if isinstance(value, dict):
        yield value
        yield from nodes(value.get("@graph"))
    elif isinstance(value, list):
        for entry in value:
            yield from nodes(entry)


def extract(html):
    parser = StructuredData()
    parser.feed(html)
    records = {}
    for block in parser.blocks:
        try:
            root = json.loads(block)
        except ValueError:
            continue
        for node in nodes(root):
            if node.get("@type") != "ItemList" or not isinstance(node.get("itemListElement"), list):
                continue
            for entry in node["itemListElement"]:
                if not isinstance(entry, dict):
                    continue
                item = entry.get("item", entry)
                if not isinstance(item, dict):
                    continue
                name, link = item.get("name"), item.get("url")
                if not isinstance(name, str) or not name.strip() or not isinstance(link, str):
                    continue
                try:
                    url = urlsplit(urljoin("https://www.yelp.com", link))
                except ValueError:
                    continue
                if url.scheme != "https" or url.netloc.lower() not in {"yelp.com", "www.yelp.com"} or not url.path.startswith("/biz/") or not url.path[5:].strip("/"):
                    continue
                canonical = "https://www.yelp.com" + url.path.rstrip("/")
                rating = item.get("aggregateRating")
                rating = rating if isinstance(rating, dict) else {}
                category = item.get("category")
                categories = ", ".join(c for c in category if isinstance(c, str)) if isinstance(category, list) else category if isinstance(category, str) else None
                records.setdefault(canonical, dict(zip(FIELDS, (
                    name.strip(), categories, rating.get("ratingValue"), rating.get("reviewCount"), canonical,
                ))))
    return list(records.values())


def csv_cell(value):
    if isinstance(value, str) and (value.startswith(("\t", "\r", "\n")) or value.lstrip().startswith(("=", "+", "-", "@"))):
        return "'" + value
    return value


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("html", type=Path)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    rows = extract(args.html.read_text(encoding="utf-8"))
    if not rows:
        cli.exit(1, "No supported Yelp listings found.\n")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "businesses.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (args.output / "businesses.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows({k: csv_cell(v) for k, v in row.items()} for row in rows)
    print(f"Exported {len(rows)} businesses.")
