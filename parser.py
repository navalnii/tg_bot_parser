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


async def parse_payloads(item_id: int, cato_id: str, link: str):
    async with httpx.AsyncClient() as client:
        resp_get = await client.get(link, headers=config.kaspi_headers)
        if resp_get.status_code == 200:
            try:
                soup = BeautifulSoup(resp_get.content, 'html.parser')
                table_payload = soup.find('div', {'class': 'mount-item-teaser _skeleton'}).find_next()
                dct = table_payload.text.split('BACKEND.components.item=')[-1]
                dct = json.loads(dct[:-1])
                payload = config.kaspi_payload
                payload['id'] = item_id
                payload['cityId'] = cato_id
                payload['product'] = dct['card']['promoConditions']
            except Exception as e:
                logger.error(f"Can't parse {link}\n{e}")
        else:
            logger.error(f'Parser could not GET payload {link}\n{resp_get.text}')

    assert resp_get.status_code == 200
    async with httpx.AsyncClient() as client:
        resp_post = await client.post(config.url_post + str(item_id), data=json.dumps(payload), headers=config.kaspi_headers)
        if resp_post.status_code == 200:
            try:
                result = json.loads(resp_post.text)
                price = float(result['offers'][0]['price'])
                seller = result['offers'][0]['merchantName']
            except Exception as e:
                logger.error(f"Can't parse {link}\n{e}")
            logger.info(f"Parsing success {price, seller, link}")
        else:
            logger.error(f'Parser could not POST price {link}\n{resp_post.text}')

    assert resp_post.status_code == 200
    async with httpx.AsyncClient() as client:
        db_resp = await client.post(config.db_service_api + 'item_price/',
                                    data=json.dumps({
                                        'price': price,
                                        'seller': seller,
                                        'item_id': int(item_id)
                                    }))
        if db_resp.status_code == 200:
            logger.info(f'POST item_price {item_id}: 200')
            return
        else:
            logger.error(f'Cound not POST item_price {item_id}\n{db_resp.text}')


async def parse_title_desc(url):
    id, desc, title = None, None, None
    try:
        with httpx.Client() as s:
            resp = s.get(url, headers=config.kaspi_headers)
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
            tasks.append(parse_payloads(item['id'], item['cato_id'], item['url']))
    await asyncio.gather(*tasks)



if __name__ == "__main__":
    # parse_title_desc('https://kadspi.kz/shop/p/apple-macbook-air-13-mgn63-seryi-100797845')
    start_time = time.monotonic()
    logger.info(f"Parser started at {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    items_lst = items()
    asyncio.run(main(items_lst))
    logger.info(f"Parser ended at {datetime.now().strftime('%d-%m-%Y %H:%M')}\nTime taken: {time.monotonic() - start_time}")



