import sqlite3
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardRemove
from pyrogram.types import CallbackQuery
from pyrogram import enums
from pycoingecko import CoinGeckoAPI
import matplotlib.pyplot as plt
from io import BytesIO
import requests
import time
admin_id = 1479016296
global days
days = 7  
app = Client("my_bot_crypto")
blocked_users = []
cg = CoinGeckoAPI()
channel_username = "@sshvpnsseller"
channel_id = "sshvpnsseller"

def create_connection():
    
    try:
        conn = sqlite3.connect("telegrambot.db")
        return conn
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return None

@app.on_message(filters.command(["start"]))
async def start_command(client, message):
    user_id = -1 
    conn = create_connection()
    if conn is not None:
        add_user(conn, user_id)
        conn.close()
    try:
        user_id = message.from_user.id
        if user_id in blocked_users:
            await message.reply("You are blocked and cannot use this bot.")
        else:
            
            chat_member = await client.get_chat_member(channel_username, user_id)

            if chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR,
                                      enums.ChatMemberStatus.MEMBER,
                                      enums.ChatMemberStatus.OWNER]:
                
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Go to Channel", url=f"https://t.me/{channel_username}")]])

                await message.reply_text("hi welcome to crypto bot tracker\nسلام به بات ارز دیجیتال خوش امدید", reply_markup=ReplyKeyboardMarkup(
                    [['channel', 'support', 'crypto', 'chart'], ['Wallet-balance']],
                    resize_keyboard=True
                ))
            else:
                await message.reply(f"برای استفاده از بات ما در چنل ما عضو شوید : https://t.me/{channel_id}")

    except Exception as e:
        await message.reply(f"برای استفاده از بات ما در چنل ما عضو شوید : https://t.me/{channel_id}")
@app.on_message(filters.command("admin") & filters.user(admin_id))
async def adminpanel(client: Client, message: Message):
        await message.reply_text("سلام ادمین خوش اومدی", reply_markup=ReplyKeyboardMarkup(
        [['🧷چنل', 'users-list', 'ads', 'block/unblock-user', 'block_list'], ['stats']],
        resize_keyboard=True
    ))
@app.on_message(filters.regex("stats")& filters.user(admin_id))
async def adminstats(client, message):
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    bot_status = "Bot is running"

    start_time = time.time()
    await message.reply("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 2)
    stats_message = f"Database Status:\n- Total Users: {user_count}\n\nBot Status:\n- {bot_status}\n\nPing: {ping_time} ms"
    await message.reply(stats_message)
async def send_user_list(message, user_data, page):
    start = (page - 1) * 10
    end = page * 10
    user_list = user_data[start:end]
    
    if user_list:
        user_list_text = '\n'.join([f"Username: {user[1]}" for user in user_list])
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Next Page", callback_data=f"next_{page}")]])
        await message.reply(f"User List (Page {page}):\n{user_list_text}", reply_markup=markup)
    else:
        await message.reply("No more users to display.")
@app.on_message(filters.regex("users-list")& filters.user(admin_id))
async def get_user_info(client, message):
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    user_data = cursor.fetchall()

    if user_data:
        
        await send_user_list(message, user_data, page=1)
    else:
        await message.reply("No users found in the database.")

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    if callback_query.data.startswith("next_"):
        page = int(callback_query.data.split("_")[1])
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user_data = cursor.fetchall()
        
        await send_user_list(callback_query.message, user_data, page=page)
def add_user(conn, user_id):
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()

        cursor.close()
    except sqlite3.Error as err:
        print(f"Error adding user: {err}")

def get_all_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        rows = cursor.fetchall()
        user_ids = [row[0] for row in rows]
        cursor.close()
        return user_ids
    except sqlite3.Error as err:
        print(f"Error getting users: {err}")
        return []
@app.on_message(filters.regex("block_list"))
async def block_list_command(client, message):
    try:
        
        blocked_users_str = '\n'.join([str(user_id) for user_id in blocked_users])

        if blocked_users_str:
            await message.reply(f"Blocked Users:\n{blocked_users_str}")
        else:
            await message.reply("No users are blocked.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
@app.on_message(filters.regex("block/unblock-user") & filters.user(admin_id))
async def adminpanel(client: Client, message: Message):
    await message.reply("برای استفاده از کامند بلاک یا ان بلاک کافیه /block و بعد اون یوزر ایدی کاربر رو وارد کنید برای ان بلاک هم فقط قبل بلاک ان بنویسید و بعدش ایدی کاربر بنویسید /unblock")

@app.on_message(filters.command("block")& filters.user(admin_id))
async def block_command(client, message):
    try:
        
        command, user_id = message.text.split(" ", 1)
        user_id = int(user_id)

        
        blocked_users.append(user_id)

        
        await message.reply(f"User with ID {user_id} has been blocked.")
    except ValueError:
        await message.reply("Please provide a valid user ID.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

def ignore_blocked_users(_, __, message):
    user_id = message.from_user.id
    return user_id not in blocked_users

def start_command_filter(_, __, message):
    user_id = message.from_user.id
    return user_id not in blocked_users and message.text == "/start"
@app.on_message(filters.command("unblock")& filters.user(admin_id))
async def unblock_command(client, message):
    try:
        
        command, user_id = message.text.split(" ", 1)
        user_id = int(user_id)

        
        if user_id in blocked_users:
            blocked_users.remove(user_id)

            
            await message.reply(f"User with ID {user_id} has been unblocked.")
        else:
            await message.reply(f"User with ID {user_id} is not blocked.")
    except ValueError:
        await message.reply("Please provide a valid user ID.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
def get_crypto_prices():
    coins = ["bitcoin", "ethereum", "cardano", "usd", "binancecoin", "ripple", "solana", "polkadot", "dogecoin", "avalanche-2", "terra-luna"]  # نمونه: ارزهای بیتکوین، اتریوم و کاردانو
    vs_currencies = "usd"  
    crypto_prices = cg.get_price(ids=coins, vs_currencies=vs_currencies)
    return crypto_prices

crypto_prices = get_crypto_prices()

message_text = "crypto  currency prices:\n"
for crypto, price_info in crypto_prices.items():
    price = price_info.get("usd")
    message_text += f"{crypto}: {price} Dollar\n"

@app.on_message(filters.regex("crypto"))
async def adminpanel(client: Client, message: Message):
        await message.reply_text(message_text, reply_markup=ReplyKeyboardMarkup(
        [['channel', 'support', 'crypto','Wallet-balance'],['chart']],
        resize_keyboard=True
    ))

def get_crypto_price_chart(crypto_name):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_name}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data.get("prices", [])
    timestamps = [price[0] for price in prices]
    prices = [price[1] for price in prices]

    
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, prices, label="Price (USD)")
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.title(f"{crypto_name} Price Chart ({days} days)")
    plt.grid(True)
    plt.legend()

    chart_image = BytesIO()
    plt.savefig(chart_image, format="png")
    chart_image.seek(0)

    return chart_image

def create_duration_keyboard():
    buttons = [
        [
            InlineKeyboardButton("7 days", callback_data="7"),
            InlineKeyboardButton("30 days", callback_data="30"),
            InlineKeyboardButton("90 days", callback_data="90")
        ]
    ]

    return InlineKeyboardMarkup(buttons)

def create_crypto_selection_keyboard():
    top_6_cryptos = [
        {"name": "bitcoin", "label": "Bitcoin"},
        {"name": "ethereum", "label": "Ethereum"},
        {"name": "cardano", "label": "Cardano"},
        {"name": "binancecoin", "label": "Binance Coin"},
        {"name": "ripple", "label": "XRP"},
        {"name": "solana", "label": "Solana"},
        {"name": "polkadot", "label": "Polkadot"},
        {"name": "dogecoin", "label": "Dogecoin"},
        {"name": "avalanche-2", "label": "Avalanche"},
        {"name": "terra-luna", "label": "Terra"},
        {"name": "usd", "label": "US Dollar"}
        
    ]

    buttons = [
        [
            InlineKeyboardButton(crypto["label"], callback_data=crypto["name"])
        ] for crypto in top_6_cryptos
    ]

    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.regex("chart"))
async def chart_command(client, message):
    global days  
    
    chat_id = message.chat.id

    
    await client.send_message(chat_id, "please chose your day time chart\n لطفا بازه زمانی خود را انتخواب کنید",
                             reply_markup=create_duration_keyboard())

@app.on_callback_query()
async def callback_query(client, query):
    global days  
    user_id = query.from_user.id
    data = query.data
    chat_id = query.message.chat.id

    if data in ["7", "30", "90"]:
        days = int(data)
        
        
        await client.send_message(chat_id, "please chose your crypto currency\n لطفا ارز خود را انتخواب کنید",
                                 reply_markup=create_crypto_selection_keyboard())
    
    elif data in ["bitcoin", "ethereum", "cardano", "binancecoin", "ripple", "usd", "solana", "polkadot", "dogecoin", "avalanche-2", "terra-luna"]:
        crypto_name = data
        
        chart_image = get_crypto_price_chart(crypto_name)

        
        await client.send_photo(user_id, photo=chart_image)

@app.on_message(filters.private & filters.regex("channel"))
async def channel(client: Client, message: Message):
    await message.reply_text("telegram channel", reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="sshvpn", url="https://t.me/sshvpnsseller")]
        ]
    ))

@app.on_message(filters.command("ads") & filters.user(admin_id))
async def send_image_with_text_from_bot(client, message):
    try:
        
        command_parts = message.text.split(" ", 2)
        
        if len(command_parts) < 3:
            await message.reply_text("لطفاً لینک عکس و متن پیام را وارد کنید.")
            return
        
        
        photo_url = command_parts[1]
        
        
        caption_text = command_parts[2]
        
        
        await app.send_photo(chat_id=message.chat.id, photo=photo_url, caption=caption_text)
    except Exception as e:
        await message.reply_text(f"خطا در ارسال عکس: {str(e)}")
@app.on_message(filters.regex("support"))
async def support(client: Client, message: Message):
    await message.reply_text("پشتیبانی", reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="click", url="https://t.me/hep_XD")]
        ]
    ))
api_url = 'https://apilist.tronscanapi.com/api/accountv2'
@app.on_message(filters.text & ~filters.command("Wallet-balance"))
async def get_balance_command(client, message):
    
    wallet_address = message.text
    
    
    params = {'address': wallet_address}
    
    
    response = requests.get(api_url, params=params)
    
    
    if response.status_code == 200:
        
        data = response.json()
        
        
        if 'balance' in data:
            
            balance = data['balance']
            await message.reply(f'Balance of {wallet_address}: {balance} TRX')


if __name__ == '__main__':
    app.run()