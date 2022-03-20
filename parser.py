import config
import json
import httpx
from bs4 import BeautifulSoup
import asyncio
import logger
import time

logger = logger.logger_init('parser')


def items():
    with httpx.Client() as s:
        resp = s.get(config.db_service_api + 'urls', follow_redirects=True)
        if resp.status_code == 200:
            data = json.loads(resp.content)
            return data['results']


async def kaspi_price_parse(link: str, item_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(link, headers=config.kaspi_headers)
        assert resp.status_code == 200
        soup = BeautifulSoup(resp.content, 'html.parser')
        table = soup.find('div', {'class': 'offer-selection__content-el _active'})
        dct = table.find('script').text.split('BACKEND.components.sellersOffers=')[-1]
        dct = json.loads(dct[:-1])
        price = float(dct['components'][0]['offers'][0]['unitSalePrice'])
        seller = dct['components'][0]['offers'][0]['name']
        db_resp = await client.post(config.db_service_api + 'item_price/',
                                    data=json.dumps({
                                        'price': price,
                                        'seller': seller,
                                        'item_id': int(item_id)
                                    }))
        if db_resp.status_code == 200:
            print(f'db_service 200, {item_id}')


async def parse_title_desc(url):
    id, desc, title = None, None, None
    try:
        with httpx.AsyncClient() as s:
            resp = await s.get(url, headers=config.kaspi_headers)
    except Exception as e:
        logger.error(f"Could not to load {url}\n{e}")
        return id, title, desc

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
        try:
            desc = soup.find('div', {'class': 'item__description-text'}).text
            table_title = soup.find('div', {'class': 'mount-item-teaser _skeleton'}).find_next()
            dct = table_title.text.split('BACKEND.components.item=')[-1]
            dct = json.loads(dct[:-1])
            title = dct['card']['title']
            id = dct['card']['id']
        except Exception as e:
            logger.error(f"Could not to parser title from {url}\n{e}")
    return id, title, desc


async def main(data: dict):
    tasks = []
    for item in data:
        if item['source'] == 'kaspi.kz':
            tasks.append(kaspi_price_parse(item['url'], item['id']))
    await asyncio.gather(*tasks)



if __name__ == "__main__":
    # a, b, c = parse_title_desc('https://kadspi.kz/shop/p/apple-macbook-air-13-mgn63-seryi-100797845/?c=710000000')
    start_time = time.monotonic()
    asyncio.run(main(items()))
    print(f"Time Taken:{time.monotonic() - start_time}")



