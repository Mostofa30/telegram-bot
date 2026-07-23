import logging
import requests
from telebot import TeleBot, types

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8664893657:AAFpVRbpZwWXElZGAXaVsDjfo20Z92k7kts"
NAGORIKPAY_API_KEY = "vMfzKDGAq6macAaJsYRztUjeibJMHTwScELb9vWEI8h6hwRL1X"

# টপ-আপ প্রোভাইডারের API (যখন প্রোভাইডার পাবেন তখন সেট করবেন)
TOPUP_API_KEY = "YOUR_TOPUP_API_KEY_HERE"
TOPUP_API_URL = "https://example-topup-provider.com/api/v1/order"

bot = TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

# ইউজারের ওয়ালেট ও স্টেট ম্যানেজমেন্ট
user_wallets = {}  # {user_id: balance}
user_states = {}   # {user_id: {"state": ..., ...}}

# ==================== ALL PACKAGES & PRICES ====================
PACKAGES = {
    # Memberships
    "p1": {"name": "WEEKLY", "price": 158},
    "p2": {"name": "MONTHLY", "price": 790},
    "p3": {"name": "2X WEEKLY", "price": 316},
    "p4": {"name": "3X WEEKLY", "price": 474},
    "p5": {"name": "2X MONTHLY", "price": 1580},
    "p6": {"name": "1X WEEKLY + 1X MONTHLY", "price": 948},
    "p7": {"name": "3X WEEKLY + 1X MONTHLY", "price": 1265},
    
    # Standard Diamonds
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
    
    # Weekly Lite
    "p20": {"name": "1X Weekly Lite", "price": 45},
    "p21": {"name": "2X Weekly Lite", "price": 90},
    "p22": {"name": "3X Weekly Lite", "price": 135},
    "p23": {"name": "5X Weekly Lite", "price": 225},
    
    # Level Up Packages
    "p24": {"name": "Level Up Package - Level 6", "price": 43},
    "p25": {"name": "Level Up Package - Level 10", "price": 75},
    "p26": {"name": "Level Up Package - Level 15", "price": 75},
    "p27": {"name": "Level Up Package - Level 20", "price": 75},
    "p28": {"name": "Level Up Package - Level 25", "price": 75},
    "p29": {"name": "Level Up Package - Level 30", "price": 105},
    "p30": {"name": "Full Level Up (1270 Diamond)", "price": 448},
}

# ==================== UPDATED NAGORIKPAY API FUNCTION ====================
def create_nagorikpay_charge(amount, user_id, purpose="Add Balance"):
    """NagorikPay Official Live API দিয়ে পেমেন্ট লিংক তৈরির ফাংশন"""
    url = "https://secure-pay.nagorikpay.com/api/payment/create"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "api_key": NAGORIKPAY_API_KEY,
        "cus_name": f"User_{user_id}",
        "cus_email": f"user{user_id}@gmail.com",
        "cus_phone": "01700000000",
        "amount": str(amount),
        "currency": "BDT",
        "desc": purpose,
        "success_url": "https://t.me/FF_TOPUP_SHOP_bot",
        "fail_url": "https://t.me/FF_TOPUP_SHOP_bot",
        "cancel_url": "https://t.me/FF_TOPUP_SHOP_bot"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        res_data = response.json()
        
        # পেমেন্ট ইউআরএল বের করা
        pay_url = res_data.get("payment_url") or res_data.get("url")
        if not pay_url and isinstance(res_data.get("data"), dict):
            pay_url = res_data.get("data", {}).get("payment_url") or res_data.get("data", {}).get("url")
            
        return pay_url
    except Exception as e:
        logging.error(f"NagorikPay API Error: {e}")
        return None

# ==================== MAIN MENU ====================
def show_main_menu(chat_id, user_id):
    balance = user_wallets.get(user_id, 0.0)
    
    text = (
        "🏬 **— FF TOPUP SHOP —**\n\n"
        f"👋 Welcome! Your Balance: **৳{balance:.2f}**\n\n"
        "⭐ **— STORE HIGHLIGHTS —** ⭐\n"
        "🔑 Premium Game Keys\n"
        "⚡ Instant Delivery 24/7\n"
        "🔒 100% Secure Payment\n"
        "🏷️ Best Prices Guaranteed\n"
        "🎁 Referral Rewards\n"
        "📞 Professional Support\n\n"
        "🚀 **Tap Shop Now to Start!**"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_shop = types.InlineKeyboardButton("💎 Shop Now", callback_data="shop_now")
    btn_orders = types.InlineKeyboardButton("📜 My Orders", callback_data="my_orders")
    btn_profile = types.InlineKeyboardButton(f"👑 Profile (৳{balance:.0f})", callback_data="profile")
    btn_add = types.InlineKeyboardButton("💳 Add Balance", callback_data="add_balance")
    btn_ref = types.InlineKeyboardButton("🤝 Referral", callback_data="referral")
    btn_spin = types.InlineKeyboardButton("🍀 Lucky Spin", callback_data="lucky_spin")
    btn_guide = types.InlineKeyboardButton("🎓 How to Use", callback_data="how_to_use")
    btn_support = types.InlineKeyboardButton("💬 Support", callback_data="support")
    
    markup.add(btn_shop)
    markup.row(btn_orders, btn_profile)
    markup.row(btn_add, btn_ref)
    markup.add(btn_spin)
    markup.add(btn_guide)
    markup.add(btn_support)
    
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# ==================== CALLBACK HANDLER ====================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    show_main_menu(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data == "shop_now":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for p_id, item in PACKAGES.items():
            btn_text = f"{item['name']} - ৳{item['price']}"
            buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{p_id}"))
        
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
        
        bot.send_message(chat_id, f"📝 আপনি সিলেক্ট করেছেন: **{selected_pack['name']}** (৳{selected_pack['price']})\n\nঅনুগ্ৰহ করে আপনার **Free Fire Player UID** লিখে পাঠান:")

    elif call.data == "pay_wallet":
        state_data = user_states.get(user_id)
        if not state_data:
            bot.send_message(chat_id, "⚠️ সেশন শেষ হয়ে গেছে! আবার শুরু করুন।")
            return
            
        price = state_data["price"]
        uid = state_data["uid"]
        balance = user_wallets.get(user_id, 0.0)
        
        if balance >= price:
            user_wallets[user_id] -= price
            bot.send_message(chat_id, "🔄 পেমেন্ট সফল! আপনার টপ-আপ প্রসেস করা হচ্ছে...")
            
            bot.send_message(
                chat_id, 
                f"✅ **টপ-আপ সফল হয়েছে!**\n\n📌 **প্যাকেজ:** {state_data['pack_name']}\n🆔 **UID:** `{uid}`\n💰 **অবশিষ্ট ব্যালেন্স:** ৳{user_wallets[user_id]:.2f}", 
                parse_mode="Markdown"
            )
            user_states.pop(user_id, None)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📱 Mobile Banking (bKash/Nagad)", callback_data="pay_mobile"))
            markup.add(types.InlineKeyboardButton("💳 Add Balance", callback_data="add_balance"))
            
            bot.send_message(chat_id, f"❌ **পর্যাপ্ত ব্যালেন্স নেই!**\nআপনার ওয়ালেটে আছে ৳{balance:.2f}, কিন্তু প্রয়োজন ৳{price}।\n\nনিচের অপশন থেকে সরাসরি পেমেন্ট বা ওয়ালেট রিচার্জ করুন:", reply_markup=markup)

    elif call.data == "pay_mobile":
        state_data = user_states.get(user_id)
        amount = state_data["price"] if state_data else 100
        pay_url = create_nagorikpay_charge(amount, user_id, purpose="Direct TopUp Payment")
        
        if pay_url:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💳 Pay Now (bKash / Nagad)", url=pay_url))
            bot.send_message(chat_id, "📱 নিচে দেয়া বাটনে চাপ দিয়ে NagorikPay-এর মাধ্যমে পেমেন্ট সম্পূর্ণ করুন:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "❌ পেমেন্ট লিংক তৈরি করতে সমস্যা হয়েছে! অনুগ্রহ করে আবার চেষ্টা করুন।")

    elif call.data == "add_balance":
        user_states[user_id] = {"state": "AWAITING_ADD_AMOUNT"}
        bot.send_message(chat_id, "💳 **ওয়ালেটে কত টাকা এড করতে চান?**\nপরিমান লিখে পাঠান (যেমন: 100, 500):")

    elif call.data == "main_menu":
        show_main_menu(chat_id, user_id)

    elif call.data == "profile":
        balance = user_wallets.get(user_id, 0.0)
        bot.send_message(chat_id, f"👤 **আপনার প্রোফাইল:**\n\n🆔 User ID: `{user_id}`\n💰 Wallet Balance: **৳{balance:.2f}**", parse_mode="Markdown")

    elif call.data in ["my_orders", "referral", "lucky_spin", "how_to_use", "support"]:
        bot.send_message(chat_id, "ℹ️ এই ফিচারটি শীঘ্রই চালু হতে যাচ্ছে!")

# ==================== TEXT MESSAGE HANDLER ====================
@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip()
    
    state_data = user_states.get(user_id)
    
    if state_data and state_data.get("state") == "AWAITING_UID":
        state_data["uid"] = text
        state_data["state"] = "AWAITING_PAYMENT"
        
        balance = user_wallets.get(user_id, 0.0)
        price = state_data["price"]
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(f"👛 Wallet Balance (আছে: ৳{balance:.2f})", callback_data="pay_wallet"))
        markup.add(types.InlineKeyboardButton("📱 Mobile Banking (bKash / Nagad)", callback_data="pay_mobile"))
        
        bot.send_message(
            chat_id,
            f"✅ **অর্ডার বিবরণী:**\n"
            f"📦 **প্যাকেজ:** {state_data['pack_name']}\n"
            f"💵 **মূল্য:** ৳{price}\n"
            f"🆔 **Player UID:** `{text}`\n\n"
            f"পেমেন্ট মাধ্যম বেছে নিন:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif state_data and state_data.get("state") == "AWAITING_ADD_AMOUNT":
        if text.isdigit():
            amount = int(text)
            pay_url = create_nagorikpay_charge(amount, user_id, purpose="Wallet Add Balance")
            
            if pay_url:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("💳 Pay Now (bKash / Nagad)", url=pay_url))
                bot.send_message(chat_id, f"💰 **৳{amount}** ওয়ালেটে এড করতে নিচের বাটনে চাপ দিন:", reply_markup=markup)
            else:
                bot.send_message(chat_id, "❌ পেমেন্ট লিংক তৈরি করা যায়নি! আবার চেষ্টা করুন।")
            user_states.pop(user_id, None)
        else:
            bot.send_message(chat_id, "❌ অনুগ্রহ করে শুধুমাত্র সঠিক সংখ্যা লিখুন (যেমন: 100)!")

# ==================== START BOT ====================
if __name__ == "__main__":
    print("FF TOPUP SHOP Bot is Running...")
    bot.infinity_polling()
