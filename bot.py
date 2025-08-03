import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, ChatNotFound
from currency_manager import CurrencyManager
from permissions import (can_manage_settings, get_user_role, is_master)
from schedule import should_announce_now, update_schedule
from owner_ui import create_menu_from_json as create_owner_menu
from setting_ui import get_admin_settings_menu, get_request_access_menu
from redis import CacheManager

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHANNEL_ID_1 = "@YourChannel1"
CHANNEL_ID_2 = "@YourChannel2"

MASTERS = {
    123456789: "M.K.1",
    987654321: "M.K.1",
    112233445: "آبتین"
}

storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode='Markdown')
dp = Dispatcher(bot, storage=storage)
cache = CacheManager()
cm = CurrencyManager(
    nobitexCurrencies=['usd', 'eur'],
    cryptoSymbols=['BTCUSDT', 'ETHUSDT', 'TRUMPUSDT', 'SHIBUSDT']
)

async def check_subscription(user_id: int) -> bool:
    try:
        member1 = await bot.get_chat_member(chat_id=CHANNEL_ID_1, user_id=user_id)
        member2 = await bot.get_chat_member(chat_id=CHANNEL_ID_2, user_id=user_id)
        return member1.is_chat_member() and member2.is_chat_member()
    except Exception as e:
        logging.error(f"Error checking subscription for {user_id}: {e}")
        return False

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(text="عضویت در کانال اول", url=f"https://t.me/{CHANNEL_ID_1[1:]}"),
            types.InlineKeyboardButton(text="عضویت در کانال دوم", url=f"https://t.me/{CHANNEL_ID_2[1:]}"),
            types.InlineKeyboardButton(text="✅ عضو شدم و تایید می‌کنم", callback_data="check_subscription")
        )
        return await message.answer("سلام! برای استفاده از ربات CHANGER_ACE، لطفاً ابتدا در دو کانال زیر عضو شوید و سپس دکمه تایید را بزنید.", reply_markup=keyboard)

    welcome_text = (
        "به ربات CHANGER_ACE خوش آمدید! 📊\n"
        "برای دریافت قیمت، نام ارز را ارسال کنید.\n\n"
        "Welcome to CHANGER_ACE Bot! 📊\n"
        "Send the name of a currency to get its price."
    )
    await message.answer(welcome_text)

@dp.callback_query_handler(text="check_subscription")
async def subscription_callback(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.delete()
        await call.answer("عضویت شما تایید شد. از ربات لذت ببرید!", show_alert=True)

    else:
        await call.answer("شما هنوز در یکی از کانال‌ها یا هر دو عضو نشده‌اید.", show_alert=True)

CURRENCY_MAP = {
    "دلار": "USD", "usd": "USD", "dollar": "USD",
    "یورو": "EUR", "eur": "EUR", "euro": "EUR",
    "بیتکوین": "BTCUSDT", "بیت کوین": "BTCUSDT", "btc": "BTCUSDT",
    "اتریوم": "ETHUSDT", "eth": "ETHUSDT",
    "ترامپ": "TRUMPUSDT", "trump": "TRUMPUSDT"
}

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    if str(message.from_user.id) in cache.get_banned_users():
        return

  if not await check_subscription(message.from_user.id):
        return await message.reply("لطفاً ابتدا در کانال‌ها عضو شوید (دستور /start را بزنید).")

    chat_settings = cache.get_chat_settings(message.chat.id)
    only_admins_can_request = chat_settings.get('request_access', 'admins') == 'admins' # پیش‌فرض فقط ادمین‌ها
    if message.chat.type != 'private' and only_admins_can_request:
        if get_user_role(message.from_user.id, message.chat.id) == 'user':
            return

    query = message.text.lower().strip()
    symbol = CURRENCY_MAP.get(query)

    if not symbol:
        if message.chat.type == 'private':
            await message.reply("ارز درخواستی یافت نشد. لطفاً نام آن را به درستی وارد کنید.")
      
        return

    try:
        cm.updateAll()
        prices = cm.getPriceDict()
        price_data = prices.get(symbol)

        if not price_data:
            raise ValueError("Price data not found for symbol")

        if "USDT" in symbol:
            response_text = f"**{symbol.replace('USDT','')}**: `${price_data['usd']:,.2f}`"
        else:
            response_text = f"**{symbol}/IRR**: `{price_data['irr']:,.0f}` تومان"

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_response = f"{response_text}\n\n*زمان*: `{timestamp}`"
        await message.answer(full_response)

    except Exception as e:
        logging.error(f"Error getting price for {symbol}: {e}")
        await message.reply("خطایی در دریافت قیمت رخ داد. لطفاً لحظاتی دیگر تلاش کنید.")
      
@dp.message_handler(is_reply=True)
async def handle_reply_actions(message: types.Message):
    user_id = message.from_user.id
    command = message.text.lower()
    
    if not is_master(user_id):
        return

    target_user_id = message.reply_to_message.from_user.id
    if command == "محروم":
        current_banned = cache.get_banned_users()
        cache.set_banned_users(list(current_banned) + [str(target_user_id)])
        await message.reply(f"کاربر {target_user_id} با موفقیت محروم شد.")

    elif command == "آزاد":
        current_banned = list(cache.get_banned_users())
        if str(target_user_id) in current_banned:
            current_banned.remove(str(target_user_id))
            cache.set_banned_users(current_banned)
            await message.reply(f"کاربر {target_user_id} با موفقیت آزاد شد.")

        else:
            await message.reply("این کاربر در لیست محرومان وجود ندارد.")

async def price_announcer_task():
    await bot.wait_until_ready()
    logging.info("Scheduled announcer task started.")
    while True:
        await asyncio.sleep(60)

async def on_startup(dispatcher):
    logging.info("Bot has been started successfully.")

if __name__ == '__main__':
    logging.info("Starting bot polling...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
