import os
import json
from dotenv import load_dotenv
import logging

import requests
from aiogram import Bot, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.utils.callback_data import CallbackData
import config

load_dotenv()

API_TOKEN = os.environ['API_TELEGRAM_TOKEN']

# webhook settings
WEBHOOK_HOST = 'https://45.129.0.139'
WEBHOOK_PATH = f'/bot{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 8443

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

callback_percent = CallbackData("name", "percent")


def reply_keyboard():
    keyboard = [
        types.InlineKeyboardButton(text=config.BUTTONS.get('under_15'), callback_data=callback_percent.new(percent='under_15')),
        types.InlineKeyboardButton(text=config.BUTTONS.get('from_15_to_25'), callback_data=callback_percent.new(percent='from_15_to_25')),
        types.InlineKeyboardButton(text=config.BUTTONS.get('upper_25'), callback_data=callback_percent.new(percent='upper_25')),
        types.InlineKeyboardButton(text="Rastaý", callback_data=callback_percent.new(percent="finish"))
    ]
    reply_markup = types.InlineKeyboardMarkup(row_width=2)
    reply_markup.add(*keyboard)
    return reply_markup


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    return await message.answer("Sálem.\nBul marketpleıs jeńildikterdi tekserý bot.\n"
                                "Bastaý úshin maǵan qandaı jeńildik mólsherin tańdańyz.", reply_markup=reply_keyboard())


@dp.callback_query_handler(callback_percent.filter(percent=["under_15", "from_15_to_25", "upper_25"]))
async def callback_discount(call: types.CallbackQuery, callback_data: dict):
    percent = callback_data["percent"]
    print(callback_data)
    # create user in db
    # if config.telegram_mode == 'webhooks':
    resp = requests.post(config.db_service_api + 'user/',
                         data=json.dumps({
                             'id': call.from_user.id,
                             'username': call.from_user.username,
                             'discount_perc': percent
                                }))
    if resp.status_code == 200:
        await call.answer(text=f"Siz {config.BUTTONS.get(percent)}% deıingi jeńildikterdi tańdadyńyz.", show_alert=True)
        await call.message.reply(f'Siz {config.BUTTONS.get(percent)}% deıingi jeńildikterdi tańdadyńyz.',
                                 reply_markup=types.ReplyKeyboardRemove())
    else:
        print(resp.text)


# @dp.callback_query_handler(callback_percent.filter(percent=["finish"]))
# async def callbacks_discount_finish(call: types.CallbackQuery):
#     user_value = user_data.get(call.from_user.id, 0)
#     await call.message.edit_text(f"Итого: {user_value}")
#     await call.answer()


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)

    # or reply INTO webhook
    return SendMessage(message.chat.id, message.text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    if config.telegram_mode == 'webhooks':
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        executor.start_polling(dp, skip_updates=True)
