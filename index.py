import asyncio
import logging
import uuid
from pathlib import Path

import aiohttp
import meilisearch

TIKA_URL = "http://localhost:9998"
SEARCH_URL = "http://localhost:7700"
INDEX = "test"
DIR = "_files"
GLOBS = ["*.docx", "*.epub", "*.html", "*.pdf", "*.ppt", "*.md"]
LOG_LEVEL = logging.INFO


async def extract_content(path):
    with open(path, "rb") as file:
        data = file.read()

    logging.info(f"Extracting {path}")
    async with aiohttp.ClientSession(TIKA_URL) as session:
        async with session.put(
            "/tika", data=data, headers={"Accept": "text/plain; charset=UTF-8"}
        ) as response:
            multiline_content = await response.text()

    logging.info(f"Done extracting {path}")
    return " ".join(
        multiline_content.splitlines()
    )  # Join line method not compatible with certain langs

async def create_index(index, path, globs):
    pass


async def main():
    logging.basicConfig(
        filename="index.log",
        filemode="w",
        encoding="utf-8",
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    logging.info("Initializing.")
    search_client = meilisearch.Client(SEARCH_URL)
    search_client.delete_index(INDEX) # Clean old index

    logging.info("Preprocessing.")
    documents = []
    contents = []
    for glob in GLOBS:
        for path in Path(DIR).rglob(glob):
            documents.append(
                {
                    "id": str(uuid.uuid4()),
                    "path": str(path),
                    "glob": glob,
                    "content": "",
                }
            )
            contents.append(extract_content(path))

    logging.info("Starting info  extraction.")
    contents = await asyncio.gather(*contents)

    logging.info(f"Done info extraction with {len(contents)} files")

    for index, content in enumerate(contents):
        documents[index]["content"] = content

    search_client.index(INDEX).add_documents(documents)


asyncio.run(main())
