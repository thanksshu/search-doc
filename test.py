import asyncio
import aiohttp
import time

TIKA_URL = "http://localhost:9998"


async def main():
    async with aiohttp.ClientSession(TIKA_URL) as session:
        with open("_files/ext-DEVONthink-html/贾明子的知乎动态 (历史文章)/贾明子回答了问题- 如何反驳「国家培养了你，学校培养了你，你却浪费这么多社会资源就做这些工作？」类似的评论-.pdf", "rb") as file:
            data = file.read()

        raw = await session.put(
            "/tika/text", data=data, headers={"Accept": "application/json; charset=UTF-8"}
        )

        info = await raw.text(encoding="utf-8")
        with open("test.json", "w", encoding="utf-8") as file:
            file.write(info)


asyncio.run(main())
