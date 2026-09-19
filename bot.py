import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# --- ТОКЕНИ ТА ПОСИЛАННЯ ---
BOT_TOKEN = "8668016567:AAE0paiP1abF7YF8Ydm2B96-lmODTPBU5Wo
"
WEB_APP_URL = "https://eror8086-cmyk.github.io/bot/"  # Ваше посилання GitHub Pages

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def main_keyboard():
    kb = [
        [InlineKeyboardButton(
            text="🚀 Запустити CryptoMiner App", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Вітаємо у **CryptoMiner App**!\n\n"
        "Натисніть кнопку нижче, щоб відкрити додаток для майнінгу криптовалют (BTC, ETH, SOL, TRX, BNB):",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def handle_ping(request):
    return web.Response(text="Bot is active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    print("Бот успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
