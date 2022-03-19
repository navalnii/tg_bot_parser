import os
import re
import ssl
import json
from dotenv import load_dotenv
from urllib.parse import urlparse
import logger

import httpx
import requests
import asyncio
import aioschedule
from aiogram import Bot, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, filters
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.utils.callback_data import CallbackData
import config


load_dotenv()

API_TOKEN = os.environ['API_TELEGRAM_TOKEN']

# webhook settings
WEBHOOK_HOST = os.environ['HOST']
WEBHOOK_PATH = f'/bot{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3001

logger = logger.logger_init('telegram')


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

callback_percent = CallbackData("name", "percent")




def reply_keyboard():
    keyboard = [
        types.InlineKeyboardButton(text=config.BUTTONS.get('under_15'), callback_data=callback_percent.new(percent='under_15')),
        types.InlineKeyboardButton(text=config.BUTTONS.get('from_15_to_25'), callback_data=callback_percent.new(percent='from_15_to_25')),
        types.InlineKeyboardButton(text=config.BUTTONS.get('upper_25'), callback_data=callback_percent.new(percent='upper_25')),
    ]
    reply_markup = types.InlineKeyboardMarkup(row_width=3)
    reply_markup.add(*keyboard)
    return reply_markup


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    return await message.answer("Sálem.\nBul marketpleıs jeńildikterdi tekserý bot.\n"
                                "Bastaý úshin maǵan qandaı jeńildik mólsherin tańdańyz.", reply_markup=reply_keyboard())


@dp.message_handler(commands=['get_items'])
async def get_items(message: types.Message):
    resp = requests.get(config.db_service_api + f'items/?user_id={message.from_user.id}')
    if resp.status_code == 200:
        ans = f'Qazirgi ýaqytta sizde kelesi ónimder bar:\n\n'
        for ind, item in enumerate(json.loads(resp.content)['results']):
            ans += f'<b>{ind+1}. {item["title"]}</b>\nlink: <u>{item["url"]}</u>\n\n'
        return await message.answer(ans, disable_web_page_preview=False)


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    pass


@dp.callback_query_handler(callback_percent.filter(percent=["under_15", "from_15_to_25", "upper_25"]))
async def callback_discount(call: types.CallbackQuery, callback_data: dict):
    percent = callback_data["percent"]
    # create user in db
    resp = requests.post(config.db_service_api + 'user/',
                         data=json.dumps({
                             'id': call.from_user.id,
                             'chat_id': call.message.chat.id,
                             'username': call.from_user.username,
                             'discount_perc': percent
                         }))
    if resp.status_code == 200:
        await call.answer(text=f"Siz {config.BUTTONS.get(percent)} deıingi jeńildikterdi tańdadyńyz.", show_alert=True)
        await call.message.delete()
    else:
        print(resp.text)


# filter url from messages
@dp.message_handler(regexp='((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
async def get_urls(message: types.Message):
    url = urlparse(message.text)
    if url.netloc == 'kaspi.kz':
        title = url.path.split('/')[-2]
        id = title.split('-')[-1]
        resp = requests.post(config.db_service_api + 'subs/',
                             params={'user_id': message.from_user.id},
                             data=json.dumps({
                                 'id': id,
                                 'title': title,
                                 'description': '',
                                 'source': url.netloc,
                                 'cato_id': re.findall('\d{7}', url.query)[0],
                                 'url': message.text
                             }))
        if resp.status_code == 200:
            await message.reply(f"Siz ónimdi parserge sátti qostyńyz")

        elif resp.status_code == 406:
            await message.reply(f"Ónim qazirdiń ózinde parserde bar. \nBúkil tizimdi kórý úshin /get_items")
            print(resp.text)


async def send_notification(message: types.Message):
    async with httpx.AsyncClient() as client:
        user_info = await client.get(config.db_service_api + 'user_info')
    if user_info['discount_perc'] == 'under_15':

        pass
    elif user_info['discount_perc'] == 'from_15_to_25':
        pass
    elif user_info['discount_perc'] == 'upper_25':
        pass



async def on_startup(_):
    asyncio.create_task(scheduler())
    # await bot.set_webhook(WEBHOOK_URL)


async def scheduler():
    aioschedule.every().day.at("12:00").do(send_notification)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_shutdown(dp):
    logger.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logger.warning('Bye!')


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)


if __name__ == '__main__':
    if config.telegram_mode == 'webhooks':
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )
    else:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


