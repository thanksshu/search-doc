import meilisearch
import json

SEARCH_URL = "http://localhost:7700"

search_client = meilisearch.Client(SEARCH_URL)
result = search_client.index("test").search("10")
with open("search_output.json", "w", encoding="utf-8") as fp:
    json.dump(result, fp, ensure_ascii=False)
