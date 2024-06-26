import os

import feedparser
from aiohttp import ClientSession
from loguru import logger
from lxml import html


async def get_news(url: str, max_results: int) -> list:
    async with ClientSession() as session:
        async with session.get(url, ssl=False) as r:
            data = await r.text()
            feed = feedparser.parse(data)
            return feed['entries'][:max_results]


async def get_last_news(url: str, max_results: int, data_path: str):
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            last_ids = set(f.read().splitlines())
    else:
        last_ids = set()

    try:
        news = await get_news(url, max_results)
        news_ids = {x['id'] for x in news}
        if last_ids == news_ids:
            return None

        with open(data_path, 'w+') as f:
            for n_id in news_ids:
                f.write(f'{n_id}\n')

        updated_news = news_ids - last_ids
        logger.info(f"After filter ids: {news_ids}")

        news_data = await get_news_data(updated_news)

        return news_data
    except Exception as e:
        logger.info(e)
        raise


async def get_news_data(links: set):
    output = []
    for link in links:
        async with ClientSession() as session:
            async with session.get(link, ssl=False) as r:
                data = await r.text()

                tree = html.fromstring(data)
                try:
                    output.append({
                        'title': tree.xpath('//*[@id="content"]/div[1]/h1/span/text()')[0],
                        'content': tree.xpath('//*[@id="content"]/div[1]//div[@class="content"]//text()'),
                        'tags': tree.xpath('//*[@id="content"]/div[1]/ul[@class="forum_tags"]//li/a/text()'),
                        'link': link,
                    })
                except Exception as e:
                    logger.info(e)
                    logger.info(f"ERROR PARSING: {link}; TREE: {tree}")
                    output.append({
                        'title': None,
                        'content': None,
                        'tags': None,
                        'link': link,
                    })

    return output
