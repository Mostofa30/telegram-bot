import logging
import requests
from telebot import TeleBot, types

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8664893657:AAGNQ30eqoOSjDgeGSSlcC39PeBAHOK_FC8"
NAGORIKPAY_API_KEY = "vMfzKDGAq6macAaJsYRztUjeibJMHTwScELb9vWEI8h6hwRL1X"

# এডমিন আইডি (⚠️ এখানে আপনার আসল Telegram Numeric ID বসান, যেমন: 123456789)
ADMIN_ID = 8801949677905 

bot = TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

# ডাটাবেজ (In-Memory Data Store)
user_wallets = {}   # {user_id: balance}
user_states = {}    # {user_id: {"state": ..., ...}}
user_orders = {}    # {order_id: {"user_id": ..., "status": ..., "amount": ...}}
order_counter = 1000

# ==================== ALL PACKAGES & PRICES ====================
PACKAGES = {
    "p1": {"name": "WEEKLY", "price": 158},
    "p2": {"name": "MONTHLY", "price": 790},
    "p3": {"name": "2X WEEKLY", "price": 316},
    "p4": {"name": "3X WEEKLY", "price": 474},
    "p5": {"name": "2X MONTHLY", "price": 1580},
    "p6": {"name": "1X WEEKLY + 1X MONTHLY", "price": 948},
    "p7": {"name": "3X WEEKLY + 1X MONTHLY", "price": 1265},
    
    "p8": {"name": "25 Diamond", "price": 22},
    "p9": {"name": "50 Diamond", "price": 36},
    "p10": {"name": "115 Diamond", "price": 79},
    "p11": {"name": "240 Diamond", "price": 158},
    "p12": {"name": "355 Diamond", "price": 237},
    "p13": {"name": "480 Diamond", "price": 316},
    "p14": {"name": "610 Diamond", "price": 400},
    "p15": {"name": "850 Diamond", "price": 558},
    "p16": {"name": "1240 Diamond", "price": 800},
    "p17": {"name": "2530 Diamond", "price": 1610},
    "p18": {"name": "5060 Diamond", "price": 3220},
    "p19": {"name": "10120 Diamond", "price": 6440},
    
    "p20": {"name": "1X Weekly Lite", "price": 45},
    "p21": {"name": "2X Weekly Lite", "price": 90},
    "p22": {"name": "3X Weekly Lite", "price": 135},
    "p23": {"name": "5X Weekly Lite", "price": 225},
    
    "p24": {"name": "Level Up Package - Level 6", "price": 43},
    "p25": {"name": "Level Up Package - Level 10", "price": 75},
    "p26": {"name": "Level Up Package - Level 15", "price": 75},
    "p27": {"name": "Level Up Package - Level 20", "price": 75},
    "p28": {"name": "Level Up Package - Level 25", "price": 75},
    "p29": {"name": "Level Up Package - Level 30", "price": 105},
    "p30": {"name": "Full Level Up (1270 Diamond)", "price": 448},
}

# ==================== UID VERIFICATION FUNCTION ====================
def verify_ff_uid(uid):
    """Free Fire Player UID ভেরিফাই করে নাম চেক করার ফাংশন"""
    if not uid.isdigit() or len(uid) < 7 or len(uid) > 12:
        return None
    
    try:
        lookup_url = f"https://ff-uid-verify.vercel.app/api/ff?uid={uid}"
        res = requests.get(lookup_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            player_name = data.get("nickname") or data.get("name") or data.get("userName")
            if player_name:
                return player_name
    except Exception as e:
        logging.error(f"UID Lookup Error: {e}")
    
    return f"Player_{uid[-4:]}"

# ==================== NAGORIKPAY API FUNCTION ====================
def create_nagorikpay_charge(amount, user_id, purpose="Add Balance"):
    """NagorikPay Official cURL Standard API"""
    url = "https://secure-pay.nagorikpay.com/api/payment/create"
    
    headers = {
        "API-KEY": NAGORIKPAY_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "success_url": "https://t.me/FF_TOPUP_SHOP_bot",
        "cancel_url": "https://t.me/FF_TOPUP_SHOP_bot",
        "webhook_url": "https://t.me/FF_TOPUP_SHOP_bot",
        "metadata": {
            "user_id": str(user_id),
            "purpose": purpose
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        pay_url = None
        if isinstance(res_data, dict):
            pay_url = res_data.get("payment_url") or res_data.get("url") or res_data.get("link")
            if not pay_url and "data" in res_data and isinstance(res_data["data"], dict):
                pay_url = res_data["data"].get("payment_url") or res_data["data"].get("url")
                
        return pay_url
    except Exception as e:
        logging.error(f"NagorikPay Exception: {e}")
        return None

# ==================== MAIN MENU ====================
def show_main_menu(chat_id, user_id):
    balance = user_wallets.get(user_id, 0.0)
    
    text = (
        "🏬 **— FF TOPUP SHOP —**\n\n"
        f"👋 Welcome! Your Balance: **৳{balance:.2f}**\n\n"
        "⭐ **— STORE HIGHLIGHTS —** ⭐\n"
        "🔑 Instant Player UID Verification\n"
        "⚡ 24/7 Top-Up Delivery\n"
        "🔒 Auto-Refund Guarantee\n\n"
        "🚀 **Tap Shop Now to Start!**"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("💎 Shop Now", callback_data="shop_now"))
    markup.row(
        types.InlineKeyboardButton("📜 My Orders", callback_data="my_orders"),
        types.InlineKeyboardButton(f"👑 Profile (৳{balance:.0f})", callback_data="profile")
    )
    markup.row(
        types.InlineKeyboardButton("💳 Add Balance", callback_data="add_balance"),
        types.InlineKeyboardButton("💬 Support", callback_data="support")
    )
    
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# ==================== HANDLERS ====================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    show_main_menu(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global order_counter
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data == "shop_now":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(f"{item['name']} - ৳{item['price']}", callback_data=f"buy_{p_id}") for p_id, item in PACKAGES.items()]
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu"))
        
        bot.edit_message_text("🛒 **পছন্দের অফারটি সিলেক্ট করুন:**", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("buy_"):
        p_id = call.data.split("_")[1]
        selected_pack = PACKAGES[p_id]
        
        user_states[user_id] = {
            "state": "AWAITING_UID",
            "pack_id": p_id,
            "pack_name": selected_pack["name"],
            "price": selected_pack["price"]
        }
        
        bot.send_message(chat_id, f"📝 **প্যাকেজ:** {selected_pack['name']} (৳{selected_pack['price']})\n\nঅনুগ্ৰহ করে আপনার **Free Fire Player UID** লিখে পাঠান:")

    elif call.data == "pay_wallet":
        state_data = user_states.get(user_id)
        if not state_data or "uid" not in state_data:
            bot.send_message(chat_id, "⚠️ অর্ডারের সেশন শেষ হয়ে গেছে! আবার চেষ্টা করুন।")
            return
            
        price = state_data["price"]
        uid = state_data["uid"]
        player_name = state_data.get("player_name", "N/A")
        balance = user_wallets.get(user_id, 0.0)
        
        if balance >= price:
            user_wallets[user_id] -= price
            order_counter += 1
            order_id = f"ORD{order_counter}"
            
            user_orders[order_id] = {
                "user_id": user_id,
                "pack_name": state_data["pack_name"],
                "price": price,
                "uid": uid,
                "player_name": player_name,
                "status": "PENDING"
            }
            
            bot.send_message(
                chat_id,
                f"⌛ **অর্ডারটি প্রসেসিংয়ে রয়েছে!**\n\n"
                f"🆔 **Order ID:** `{order_id}`\n"
                f"📦 **Package:** {state_data['pack_name']}\n"
                f"🎮 **Player Name:** `{player_name}`\n"
                f"🔢 **UID:** `{uid}`\n"
                f"📊 **Status:** `PENDING ⏳`\n\n"
                f"অবশিষ্ট ওয়ালেট ব্যালেন্স: ৳{user_wallets[user_id]:.2f}",
                parse_mode="Markdown"
            )
            
            admin_markup = types.InlineKeyboardMarkup()
            admin_markup.row(
                types.InlineKeyboardButton("✅ Complete", callback_data=f"adm_complete_{order_id}"),
                types.InlineKeyboardButton("❌ Cancel & Refund", callback_data=f"adm_refund_{order_id}")
            )
            
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"📩 **নতুন অর্ডার এসেছে!**\n\n"
                    f"Order ID: `{order_id}`\n"
                    f"User ID: `{user_id}`\n"
                    f"Player Name: `{player_name}`\n"
                    f"UID: `{uid}`\n"
                    f"Item: {state_data['pack_name']} (৳{price})",
                    parse_mode="Markdown",
                    reply_markup=admin_markup
                )
            except Exception:
                pass
                
            user_states.pop(user_id, None)
        else:
            bot.send_message(chat_id, f"❌ **পর্যাপ্ত ব্যালেন্স নেই!**\nআপনার ব্যালেন্স: ৳{balance:.2f} | প্রয়োজন: ৳{price}\n\n'Add Balance' থেকে রিচার্জ করুন।")

    elif call.data == "pay_mobile":
        state_data = user_states.get(user_id)
        amount = state_data["price"] if state_data else 100
        pay_url = create_nagorikpay_charge(amount, user_id, purpose="Direct TopUp")
        
        if pay_url:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💳 Pay via NagorikPay", url=pay_url))
            bot.send_message(chat_id, "📱 পেমেন্ট সম্পন্ন করতে নিচের লিংকে ক্লিক করুন:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "❌ পেমেন্ট লিংক তৈরি করা যায়নি! অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।")

    # ==================== ADMIN ORDER MANAGEMENT ====================
    elif call.data.startswith("adm_complete_"):
        order_id = call.data.split("_")[2]
        order = user_orders.get(order_id)
        
        if order and order["status"] == "PENDING":
            order["status"] = "COMPLETED"
            bot.send_message(chat_id, f"✅ Order `{order_id}` marked as COMPLETED.")
            
            bot.send_message(
                order["user_id"],
                f"🎉 **আপনার অর্ডারটি কমপ্লিট হয়েছে!**\n\n"
                f"🆔 **Order ID:** `{order_id}`\n"
                f"📦 **Package:** {order['pack_name']}\n"
                f"📊 **Status:** `COMPLETED ✅`",
                parse_mode="Markdown"
            )

    elif call.data.startswith("adm_refund_"):
        order_id = call.data.split("_")[2]
        order = user_orders.get(order_id)
        
        if order and order["status"] == "PENDING":
            order["status"] = "CANCELLED"
            refund_amount = order["price"]
            u_id = order["user_id"]
            
            user_wallets[u_id] = user_wallets.get(u_id, 0.0) + refund_amount
            
            bot.send_message(chat_id, f"❌ Order `{order_id}` Cancelled & Refunded ৳{refund_amount}.")
            
            bot.send_message(
                u_id,
                f"⚠️ **আপনার অর্ডারটি বাতিল করা হয়েছে!**\n\n"
                f"🆔 **Order ID:** `{order_id}`\n"
                f"💰 **Refunded Amount:** ৳{refund_amount}\n"
                f"📊 **Status:** `REFUNDED ↩️`\n\n"
                f"টাকা আপনার ওয়ালেটে ফেরত যোগ করা হয়েছে।",
                parse_mode="Markdown"
            )

    elif call.data == "add_balance":
        user_states[user_id] = {"state": "AWAITING_ADD_AMOUNT"}
        bot.send_message(chat_id, "💳 **ওয়ালেটে কত টাকা এড করতে চান?**\nপরিমান লিখে পাঠান (যেমন: 100, 500):")

    elif call.data == "my_orders":
        my_list = [f"🆔 `{o_id}` - {info['pack_name']} | Status: `{info['status']}`" for o_id, info in user_orders.items() if info["user_id"] == user_id]
        if my_list:
            bot.send_message(chat_id, "📜 **আপনার সাম্প্রতিক অর্ডারসমূহ:**\n\n" + "\n".join(my_list), parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "ℹ️ আপনার কোনো অর্ডার পাওয়া যায়নি।")

    elif call.data == "main_menu":
        show_main_menu(chat_id, user_id)

    elif call.data == "profile":
        balance = user_wallets.get(user_id, 0.0)
        bot.send_message(chat_id, f"👤 **আপনার প্রোফাইল:**\n\n🆔 User ID: `{user_id}`\n💰 Balance: **৳{balance:.2f}**", parse_mode="Markdown")

# ==================== TEXT MESSAGE HANDLER ====================
@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip()
    
    state_data = user_states.get(user_id)
    
    if state_data and state_data.get("state") == "AWAITING_UID":
        bot.send_message(chat_id, "🔍 **UID ভেরিফাই করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...**")
        
        player_name = verify_ff_uid(text)
        
        if player_name:
            state_data["uid"] = text
            state_data["player_name"] = player_name
            state_data["state"] = "AWAITING_PAYMENT"
            
            balance = user_wallets.get(user_id, 0.0)
            price = state_data["price"]
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(f"👛 Wallet Balance (আছে: ৳{balance:.2f})", callback_data="pay_wallet"))
            markup.add(types.InlineKeyboardButton("📱 Mobile Banking (NagorikPay)", callback_data="pay_mobile"))
            
            bot.send_message(
                chat_id,
                f"✅ **একাউন্ট ভেরিফাইড হয়েছে!**\n\n"
                f"🎮 **Player Name:** `{player_name}`\n"
                f"🆔 **Player UID:** `{text}`\n"
                f"📦 **Package:** {state_data['pack_name']}\n"
                f"💵 **Price:** ৳{price}\n\n"
                f"পেমেন্ট মাধ্যম সিলেক্ট করুন:",
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            bot.send_message(chat_id, "❌ **ভুল UID!**\nঅনুগ্রহ করে সঠিক Free Fire Player UID লিখে পাঠান:")

    elif state_data and state_data.get("state") == "AWAITING_ADD_AMOUNT":
        if text.isdigit():
            amount = int(text)
            pay_url = create_nagorikpay_charge(amount, user_id, purpose="Wallet Recharge")
            
            if pay_url:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("💳 Pay Now (bKash / Nagad)", url=pay_url))
                bot.send_message(chat_id, f"💰 **৳{amount}** ওয়ালেটে এড করতে নিচের বাটনে ক্লিক করুন:", reply_markup=markup)
            else:
                bot.send_message(chat_id, "❌ পেমেন্ট লিংক তৈরি করা যায়নি! আবার চেষ্টা করুন।")
            user_states.pop(user_id, None)
        else:
            bot.send_message(chat_id, "❌ অনুগ্রহ করে শুধুমাত্র সঠিক সংখ্যা লিখুন (যেমন: 100)!")

# ==================== START BOT ====================
if __name__ == "__main__":
    print("FF TOPUP SHOP Bot is Running...")
    bot.infinity_polling()
