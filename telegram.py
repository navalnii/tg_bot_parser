import os
import re
import ssl
import json
from datetime import datetime
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
import parser

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
    await message.answer(
        "Sálem!\nBul marketpleıs jeńildikterdi tekserý bot.\n"
        "Endi bot taýarlardyń baǵasyn belgileýi úshin, onyń url jiberińiz.\n"
        "\"https://kaspi.kz/shop/p/apple-macbook-air-13-mgn63-seryi-100797845/?c=710000000\"\n"
        "Barlyq ónimder tizimin kórý úshin /get_items jazyńyz.\n"
        "Bot toqtatý úshin /unsubscribe jazyńyz.\n",
        disable_web_page_preview=True)
    await message.answer_photo(photo=open(config.telegram_img_path + '1_entry.jpeg', 'rb'))
    await message.answer_photo(photo=open(config.telegram_img_path + '2_entry.jpeg', 'rb'))
    await message.answer_photo(photo=open(config.telegram_img_path + '3_entry.jpeg', 'rb'))
    await message.answer("Bastaý úshin jeńildik mólsherin tańdańyz.", reply_markup=reply_keyboard())
    return


@dp.message_handler(commands=['get_items'])
async def get_items(message: types.Message):
    resp = requests.get(config.db_service_api + f'items_user/?user_id={message.from_user.id}')
    if resp.status_code == 200:
        logger.info(f'GET items_user/?user_id={message.from_user.id}: 200')
        ans = f'Qazirgi ýaqytta sizde kelesi ónimder bar:\n\n'
        for ind, item in enumerate(json.loads(resp.content)['results']):
            ans += f'<b>{ind+1}. {item["title"]}</b>\n<u>{item["url"]}</u>\n\n'
        return await message.answer(ans, disable_web_page_preview=True)
    else:
        logger.error(f'Could not GET items_user/?user_id={message.from_user.id}\n{resp.text}')
        return


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    resp = requests.post(config.db_service_api + 'user/',
                         data=json.dumps({
                             'id': message.from_user.id,
                             'chat_id': message.chat.id,
                             'username': message.from_user.username,
                             'is_active': False
                         }))
    if resp.status_code == 200:
        await message.answer(text=f"Bot sátti toqtatyldy")
        logger.info(f'User {message.from_user.username} unsubscribeted')
    else:
        logger.error(f'Could not POST user {message.from_user.id}\n{resp.text}')
    return


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
        logger.info(f'User {call.from_user.username} started bot')
        await call.answer(text=f"Siz {config.BUTTONS.get(percent)} deıingi jeńildikterdi tańdadyńyz.",
                          show_alert=True)
        await call.message.delete()
    else:
        logger.error(f'Could not POST user {call.from_user.id}\n{resp.text}')
    return


# filter url from messages
@dp.message_handler(regexp='((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
async def get_urls(message: types.Message):
    url = urlparse(message.text)
    id, title, desc = await parser.parse_title_desc(message.text)
    if url.netloc == 'kaspi.kz':
        if not re.findall('\d{7}', url.query):
            await message.reply(f"Url qala tabylmady. Tómendegi sýrettegideı qalany tańdańyz")
            await message.answer_photo(photo=open(config.telegram_img_path + '1_faq.jpeg', 'rb'))
            return
        resp = requests.post(config.db_service_api + 'subs/',
                             params={'user_id': message.from_user.id},
                             data=json.dumps({
                                 'id': id,
                                 'title': title,
                                 'description': desc,
                                 'source': url.netloc,
                                 'cato_id': re.findall('\d{7}', url.query)[0],
                                 'url': message.text
                             }))
        if resp.status_code == 200:
            logger.info(f'User {message.from_user.username} added item {title}')
            return await message.reply(f"Siz ónimdi parserge sátti qostyńyz")

        elif resp.status_code == 406:
            return await message.reply(f"Ónim qazirdiń ózinde parserde bar. \nBúkil tizimdi kórý úshin /get_items")
    else:
        return await message.reply(f"Alynǵan url anyqtalmady.")


async def send_notification():
    with httpx.Client() as client:
        users_list = client.get(config.db_service_api + 'users')
    if users_list.status_code == 200:
        users_list = json.loads(users_list.content)
        for user in users_list['results']:
            try:
                text = 'Kelesi jeńildikter tabyldy:\n\n'
                async with httpx.AsyncClient() as client:
                    user_items = await client.get(config.db_service_api + f'get_item_price/?user_id={user["id"]}')
                    user_items = json.loads(user_items.content)
                for ind, user_item in enumerate(user_items):
                    text += f'<b>{ind + 1}) {user_item["item"]["title"]}</b>\n'
                    text += f'baǵasy - {user_item["price"][0]["price"]} - {user_item["price"][0]["seller"]}     '
                    text += f'(eski - {user_item["price"][1]["price"]} - {user_item["price"][1]["seller"]})\n'
                    text += f'{user_item["item"]["url"]}\n\n'
                if user_items:
                    logger.info(f'User {user["username"]} received notifications at {datetime.now().strftime("%Y-%m-%d %H:%M")}')
                    await dp.bot.send_message(chat_id=user["id"], text=text, disable_web_page_preview=True)
            except Exception as e:
                logger.error(f'Could not send notification {user["id"]}\n{e}')
                continue
    else:
        logger.error(f'Could not GET users\n{users_list.text}')
    return


async def on_startup(_):
    asyncio.create_task(scheduler())
    # await bot.set_webhook(WEBHOOK_URL)


async def scheduler():
    aioschedule.every().day.at("15:15").do(send_notification)
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


