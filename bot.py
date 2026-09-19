import asyncio
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiocryptopay import AioCryptoPay, Networks

# --- ВСТАВТЕ ВАШІ ТОКЕНИ СЮДИ ---
BOT_TOKEN = "8668016567:AAEFfz-VOoRli10CXpl-3JxYQmj92Ofmxic"
CRYPTO_PAY_TOKEN = "636094:AAShd4R213wDF5ZY8FZHVfJ02C5RDVqQ7ok"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
crypto = AioCryptoPay(token=CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)

users_db = {}

def get_user_data(user_id: int):
    now = time.time()
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "hashrate": 1.0, "last_update": now}
    else:
        time_passed = now - users_db[user_id]["last_update"]
        mined = time_passed * (users_db[user_id]["hashrate"] * 0.00001)
        users_db[user_id]["balance"] += mined
        users_db[user_id]["last_update"] = now
    return users_db[user_id]

def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⛏ Майнити / Оновити", callback_data="refresh")],
            [InlineKeyboardButton(text="⚡️ Збільшити хешрейт (+10 MH/s за 5 USDT)", callback_data="buy_hashrate")]
        ]
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    data = get_user_data(message.from_user.id)
    await message.answer(
        f"👋 Вітаємо у майнінг-симуляторі!\n\n"
        f"📊 **Ваша статистика:**\n"
        f"• Баланс: `{data['balance']:.6f}` COIN\n"
        f"• Швидкість (Хешрейт): `{data['hashrate']:.1f}` MH/s\n\n"
        f"Майнінг працює пасивно!",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

@dp.callback_query(F.data == "refresh")
async def process_refresh(callback: types.CallbackQuery):
    data = get_user_data(callback.from_user.id)
    await callback.message.edit_text(
        f"👋 Вітаємо у майнінг-симуляторі!\n\n"
        f"📊 **Ваша статистика (Оновлено):**\n"
        f"• Баланс: `{data['balance']:.6f}` COIN\n"
        f"• Швидкість (Хешрейт): `{data['hashrate']:.1f}` MH/s\n\n"
        f"Майнінг працює пасивно!",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    await callback.answer("Дані оновлено!")

@dp.callback_query(F.data == "buy_hashrate")
async def process_buy_hashrate(callback: types.CallbackQuery):
    invoice = await crypto.create_invoice(
        asset='USDT', 
        amount=5.0, 
        description='Покупка +10 MH/s хешрейту',
        payload=str(callback.from_user.id)
    )
    pay_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатити 5 USDT", url=invoice.bot_invoice_url)],
            [InlineKeyboardButton(text="🔄 Перевірити оплату", callback_data=f"check_{invoice.invoice_id}")]
        ]
    )
    await callback.message.answer(
        "Для збільшення швидкості на **+10 MH/s**, оплатіть інвойс на **5 USDT** нижче:",
        parse_mode="Markdown",
        reply_markup=pay_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("check_"))
async def process_check_payment(callback: types.CallbackQuery):
    invoice_id = int(callback.data.split("_")[1])
    invoices = await crypto.get_invoices(invoice_ids=invoice_id)
    if invoices and invoices.status == 'paid':
        data = get_user_data(callback.from_user.id)
        data["hashrate"] += 10.0
        await callback.message.edit_text(
            f"✅ **Оплата успішна!**\n\n"
            f"Ваш хешрейт збільшено на 10 MH/s.\n"
            f"Поточний хешрейт: `{data['hashrate']:.1f}` MH/s",
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Оплату ще не підтверджено.", show_alert=True)

async def main():
    print("Бот запущений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
