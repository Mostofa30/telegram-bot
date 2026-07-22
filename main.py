import telebot
import requests
from telebot import types

# ==================== ১. কনফিগারেশন ====================
BOT_TOKEN = "8664893657:AAEXNHTYGWwqEKi-oLOlrYwz7zKEMa0alYE"  # আপনার BotFather টোকেন
NAGORIKPAY_API_KEY = "vMfzKDGAq6macAaJsYRztUjeibJMHTwScELb9vWEI8h6hwRL1X"  # NagorikPay Brand Key
API_CREATE_URL = "https://nagorikpay.com/api/v1/create-charge"

bot = telebot.TeleBot(BOT_TOKEN)
user_balances = {}

def get_balance(user_id):
    return user_balances.get(user_id, 0.0)

# ==================== ২. স্টার্ট কমান্ড ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    balance = get_balance(user_id)

    welcome_text = (
        f"👋 **হ্যালো {first_name}, আমাদের বটে আপনাকে স্বাগতম!**\n\n"
        f"💰 **আপনার বর্তমান ব্যালেন্স:** ৳{balance:.2f}\n\n"
        f"নিচের মেনু থেকে আপনার প্রয়োজনীয় অপশনটি নির্বাচন করুন:"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_shop = types.InlineKeyboardButton("💎 Shop Now", callback_data="shop")
    btn_balance = types.InlineKeyboardButton("💳 Add Balance", callback_data="add_balance")
    btn_profile = types.InlineKeyboardButton("👤 Profile", callback_data="profile")
    btn_support = types.InlineKeyboardButton("💬 Support", callback_data="support")

    markup.add(btn_shop)
    markup.add(btn_balance, btn_profile)
    markup.add(btn_support)

    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ==================== ৩. কলব্যাক হ্যান্ডলার ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == "add_balance":
        msg = bot.send_message(
            call.message.chat.id,
            "💳 **কত টাকা ডিপোজিট করতে চান?**\n\n"
            "টাকার পরিমাণ লিখে মেসেজ পাঠান (যেমন: 50, 100, 500):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_deposit_amount)

    elif call.data == "profile":
        balance = get_balance(user_id)
        profile_text = f"👤 **প্রোফাইল വിവരণ:**\n\n🆔 **User ID:** `{user_id}`\n💰 **Balance:** ৳{balance:.2f}"
        bot.send_message(call.message.chat.id, profile_text, parse_mode="Markdown")

    elif call.data == "shop":
        bot.send_message(call.message.chat.id, "🛒 **শপ সেকশন:** বর্তমানে কোনো আইটেম নেই।")

    elif call.data == "support":
        bot.send_message(call.message.chat.id, "💬 এডমিনের সাথে যোগাযোগ করুন: @your_admin_username")

# ==================== ৪. পেমেন্ট তৈরি ====================
def process_deposit_amount(message):
    try:
        amount = float(message.text.strip())
        if amount < 10:
            bot.reply_to(message, "❌ **সর্বনিম্ন ১০ টাকা ডিপোজিট করতে পারবেন।**", parse_mode="Markdown")
            return

        payload = {
            "api_key": NAGORIKPAY_API_KEY,
            "amount": amount,
            "cus_name": message.from_user.first_name or "Customer",
            "cus_email": "customer@gmail.com",
            "cus_number": "01700000000",
            "currency": "BDT",
            "success_url": "https://t.me",
            "cancel_url": "https://t.me"
        }

        response = requests.post(API_CREATE_URL, data=payload)
        res_data = response.json()

        payment_url = res_data.get("payment_url") or res_data.get("url") or res_data.get("checkout_url")

        if (res_data.get("status") == "success" or res_data.get("status") is True) and payment_url:
            markup = types.InlineKeyboardMarkup()
            btn_pay = types.InlineKeyboardButton("💳 Pay Now (bKash/Nagad/Rocket)", url=payment_url)
            markup.add(btn_pay)

            bot.send_message(
                message.chat.id,
                f"✅ **৳{amount:.2f} টাকার ডিপোজিট অর্ডার তৈরি হয়েছে!**\n\n"
                f"পেমেন্ট করতে নিচের **Pay Now** বাটনে ক্লিক করুন:",
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            error_msg = res_data.get("message") or res_data.get("error") or "পেমেন্ট গেটওয়েতে সমস্যা হয়েছে।"
            bot.reply_to(message, f"❌ **পেমেন্ট তৈরি করা যায়নি:** {error_msg}")

    except ValueError:
        bot.reply_to(message, "❌ **অকার্যকর ইনপুট!** শুধু সংখ্যা লিখে পাঠান।")
    except Exception as e:
        bot.reply_to(message, f"❌ এরর: {str(e)}")

# ==================== ৫. রান করা ====================
if __name__ == "__main__":
    print("🤖 Bot is starting on Render...")
    bot.infinity_polling()
