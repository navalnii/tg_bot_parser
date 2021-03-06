import config
import json
import httpx
from datetime import datetime
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
        logger.error(f'Cound not GET urls\n{resp.text}')


async def log_request(request):
    logger.info(f"Request event hook: {request.method} {request.url} - Waiting for response")


async def log_response(response):
    request = response.request
    logger.info(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")


async def parse_kaspi_price(item_id: int, cato_id: str, link: str):
    price, seller = None, None
    async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]},
                                 timeout=60.0) as client:
        resp_get = await client.get(link, headers=config.kaspi_headers)
        assert resp_get.status_code == 200
        try:
            soup = BeautifulSoup(resp_get.content, 'html.parser')
            table_payload = soup.find('div', {'class': 'mount-item-teaser _skeleton'}).find_next()
            dct = table_payload.text.split('BACKEND.components.item=')[-1]
            dct = json.loads(dct[:-1])
            payload = config.kaspi_payload
            payload['id'] = item_id
            payload['cityId'] = cato_id
            payload['product'] = dct['card']['promoConditions']
        except:
            logger.exception(f"Can't parse GET call {link}")
        resp_post = await client.post(config.url_post + str(item_id),
                                      data=json.dumps(payload),
                                      headers=config.kaspi_headers)
        assert resp_post.status_code == 200
        result = json.loads(resp_post.text)
        try:
            price = float(result['offers'][0]['price'])
            seller = result['offers'][0]['merchantName']
            logger.info(f"Parsing success {price, seller, link}")
        except:
            logger.exception(f"Can't parse POST call {link}")
    if price and seller:
        async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}) as client:
            resp_db = await client.post(config.db_service_api + 'item_price/',
                                        data=json.dumps({
                                            'price': price,
                                            'seller': seller,
                                            'item_id': int(item_id)
                                        }))
            if resp_db.status_code == 200:
                logger.info(f'Successful inserted into db {item_id} {price}')
            else:
                logger.error(f'Failed to insert into db {item_id}', exc_info=True)


async def parse_kaspi_title_desc(url):
    id, desc, title = None, None, None
    async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}, timeout=60.0) as s:
        resp = await s.get(url, headers=config.kaspi_headers)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
        try:
            desc = soup.find('div', {'class': 'item__description-text'}).text
            table_title = soup.find('div', {'class': 'mount-item-teaser _skeleton'}).find_next()
            dct = table_title.text.split('BACKEND.components.item=')[-1]
            dct = json.loads(dct[:-1])
            title = dct['card']['title']
            id = dct['card']['id']
        except:
            logger.exception(f'Could not to parser title from {url}')
    else:
        logger.error(f'Could not to load {url}', exc_info=True)
    return id, title, desc


async def main(data: dict):
    tasks = []
    for item in data:
        if item['source'] == 'kaspi.kz':
            tasks.append(parse_kaspi_price(item['id'], item['cato_id'], item['url']))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # parse_title_desc('https://kaspi.kz/shop/p/apple-iphone-13-128gb-chernyi-102298404/?c=710000000')
    start_time = time.monotonic()
    logger.info(f"\n\nParser started at {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    items_lst = items()
    asyncio.run(main(items_lst[7:11]))
    logger.info(f"Parser ended at {datetime.now().strftime('%d-%m-%Y %H:%M')}\nTime taken: {time.monotonic() - start_time}\n")



