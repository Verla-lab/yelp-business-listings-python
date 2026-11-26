### TL;DR

- Extract business-listing metadata from a saved Yelp search HTML snapshot.
- Export business name, categories, rating, review count, and Yelp business URL to CSV or JSON.
- Parse embedded JSON-LD when present; report unsupported markup instead of silently returning an empty report.
- Run the example offline against a synthetic page.

## Build a local business shortlist

If you're comparing coffee shops in a neighborhood, a spreadsheet lets you sort listings by rating or review count without reopening each business page. This parser reads a local HTML file. It looks for a JSON-LD `ItemList` whose entries contain business details and Yelp `/biz/` links.

The included snapshot is synthetic. This parser has not been validated against current Yelp search pages, which may not expose this structure. Use the example to learn the extraction workflow, not as a claim of live compatibility.

## Run the parser

```sh
python3 extract.py fixtures/yelp-search.html sample-output
python3 -m unittest -v
```

The example exports one business to `businesses.csv` and `businesses.json`. Missing ratings and review counts stay blank rather than becoming zero. Duplicate business links are collapsed after query strings and fragments are removed.

## Responsible use

Only process snapshots you are authorized to use. The tool does not sign in, send requests to Yelp, collect reviewer profiles or review text, or work around access restrictions. If a snapshot contains an access or verification page, this parser will not produce a report unless it contains supported listing data.

## FAQ

### Q: Can I give the tool a Yelp URL?

No. The input is a saved HTML file.

### Q: Why does my snapshot show “No supported Yelp listings found”?

The parser found no business entries matching its JSON-LD contract. This may mean a different layout, an incomplete snapshot, or an access page; it does not mean the search returned no businesses.

### Q: Are the demo businesses real?

No. The fixture illustrates the expected input and output, not live Yelp data.

### Q: Does the example include individual reviews?

No. It keeps only aggregate rating and review counts.

### Q: Do I need to install packages?

No. The example uses the Python standard library.
