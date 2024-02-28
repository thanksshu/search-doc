import asyncio
import logging
import uuid
from pathlib import Path

import aiohttp
from lingua import Language, LanguageDetectorBuilder
from meilisearch import Client as MeilisearchClient
from meilisearch.errors import (MeilisearchApiError,
                                MeilisearchCommunicationError,
                                MeilisearchTimeoutError)

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
            "/tika", data=data, headers={"Accept": "application/json; charset=UTF-8"}
        ) as response:
            multiline_content = ""
            match response.status:
                case 200:
                    multiline_content = await response.text()
                case 204:
                    logging.warning(f"Empty {path}")
                case 422:
                    raise Exception(f"Unprocessable {path}")
                case 500:
                    raise Exception(f"Error while processing {path}")

    logging.info(f"Done extracting {path}")
    return " ".join(
        multiline_content.splitlines()
    )  # Join line method not compatible with certain langs


async def main():
    logging.basicConfig(
        filename="index.log",
        filemode="w",
        encoding="utf-8",
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    logging.info("Starting info extraction.")
    extractions = []
    for glob in GLOBS:
        for path in Path(DIR).rglob(glob):
            extractions.append(
                {
                    "path": str(path),  # Primary Key
                    "glob": glob,
                    "extraction_result": {"success": False, "text":""},
                }
            )
            contents.append(extract_content(path))

    contents = await asyncio.gather(*contents)

    logging.info(f"Done info extraction with {len(contents)} files")

    logging.info("Generating documents")
    for index, content in enumerate(contents):
        extractions[index]["content"] = content
    logging.info("Done generating documents")

    logging.info(f"Adding documents to index queue")
    search_client = MeilisearchClient(SEARCH_URL)
    search_client.delete_index(INDEX)  # Clear old index, need better impl
    search_client.create_index(INDEX, {"primaryKey": "path"})
    search_client.index(INDEX).update_settings(
        {
            "searchableAttributes": ["path", "content", "glob"],
            "displayedAttributes": ["path", "content", "glob"],
            "filterableAttributes": ["glob"],
        }
    )
    search_client.index(INDEX).add_documents(extractions)
    logging.info(f"Done adding documents to index queue")


asyncio.run(main())
