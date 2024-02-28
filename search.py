import meilisearch
import json

SEARCH_URL = "http://localhost:7700"

search_client = meilisearch.Client(SEARCH_URL)
result = search_client.index("test").search(
    "10",
    {
        "facets": ["glob"],
        "filter": "",
        "attributesToCrop": ["content"],
        "cropLength": 8,
        "attributesToHighlight": ["overview"],
        "highlightPreTag": "<em>",
        "highlightPostTag": "</em>",
    },
)
with open("search_output.json", "w", encoding="utf-8") as fp:
    json.dump(result, fp, ensure_ascii=False)
