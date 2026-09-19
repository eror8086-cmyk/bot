import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiocryptopay import AioCryptoPay, Networks

# --- ТОКЕНИ ---
BOT_TOKEN = "8668016567:AAE0paiP1abF7YF8Ydm2B96-lmODTPBU5Wo"
CRYPTO_PAY_TOKEN = "636094:AAShd4R213wDF5ZY8FZHVfJ02C5RDVqQ7ok"

# Фікс циклу подій для Python 3.14
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
crypto = AioCryptoPay(token=CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)

users_db = {}

def get_user_data(user_id):
    if user_id not in users_db:
        users_db[user_id] = {"hashrate": 10, "balance": 0.0}
    return users_db[user_id]

def main_keyboard():
    kb = [
        [InlineKeyboardButton(text="⛏ Майнінг", callback_data="mining")],
        [InlineKeyboardButton(text="⚡ Купити хешрейт (USDT)", callback_data="buy_hashrate")],
        [InlineKeyboardButton(text="💰 Профіль", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    get_user_data(message.from_user.id)
    await message.answer(
        "👋 Вітаємо у майнінг-боті!\n\nОтримуйте пасивний дохід та збільшуйте свій хешрейт.",
        reply_markup=main_keyboard()
    )

@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    data = get_user_data(callback.from_user.id)
    text = (
        f"📊 **Ваш профіль:**\n\n"
        f"⚡ Хешрейт: **{data['hashrate']} GH/s**\n"
        f"💰 Баланс: **{data['balance']:.4f} USDT**"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

@dp.callback_query(F.data == "buy_hashrate")
async def buy_hashrate_handler(callback: types.CallbackQuery):
    invoice = await crypto.create_invoice(asset="USDT", amount=1.0, description="Купівля +50 GH/s хешрейту")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 1 USDT", url=invoice.bot_invoice_url)],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="profile")]
    ])
    
    await callback.message.edit_text(
        "⚡ **Збільшення хешрейту:**\n\nЦіна: **1 USDT** за **+50 GH/s**.\nНатисніть кнопку нижче для оплати:",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
