import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# =====================================================================
# 1. RENDER እንዳይዘጋ የሚያደርግ የ FLASK ሰርቨር (PORT BINDING)
# =====================================================================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# =====================================================================
# 2. የቦቱ ዋና ቅንብር (CONFIGURATION)
# =====================================================================
API_TOKEN = '8709684996:AAEJOSnQZehV6T9ED2lP6HXeKVY5QJ9C-OQ'
bot = telebot.TeleBot(API_TOKEN)

bot.delete_webhook()
user_sessions = {}

# =====================================================================
# 3. የቦቱ ትእዛዞች እና ፍሰቶች (COMMANDS & FLOWS)
# =====================================================================

# --- 1ኛ ደረጃ፦ የ START ትእዛዝ (መግዛት ወይም መሸጥ ምርጫ መጀመሪያ ይመጣል) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {} # ሰsession መክፈት
    
    welcome_text = "መጀመሪያ እንኳን በሰላም መጡ! በዚህ ቦት ላይ ምን ማድረግ ነው የፈለጉት?"
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_buy = types.KeyboardButton('🛒 መግዛት')
    btn_sell = types.KeyboardButton('💰 መሸጥ')
    markup.add(btn_buy, btn_sell)
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

# --- 2ኛ ደረጃ፦ ምርጫዎችን ማስተናገጃ (🛒 መግዛት ወይም 💰 መሸጥ) ---
@bot.message_handler(func=lambda message: message.text in ['🛒 መግዛት', '💰 መሸጥ'])
def handle_buy_sell(message):
    chat_id = message.chat.id
    
    if message.text == '🛒 መግዛት':
        # 🔗 ለተጠቃሚው የቴሌግራም ቻናል እና የዌብሳይት ሊንክ የሚሰጥበት ማሳያ (ባዶ ቦታዎች)
        buy_text = (
            "🛒 እቃዎችን ወይም ቤቶችን ለመግዛት የሚከተሉትን አማራጮች ይጠቀሙ፦\n\n"
            "🌐 የዌብሳይታችን ሊንክ፦\n"
            "እዚህ ላይ የዌብሳይትህን ሊንክ አስገባ\n\n"
            "📢 የቴሌግራም ቻናላችን፦\n"
            "እዚህ ላይ የቴሌግራም ቻናልህን ሊንክ አስገባ"
        )
        
        # ተጠቃሚው ወደ ኋላ መመለስ ከፈለገ የሚጠቀምበት ቁልፍ
        back_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        back_markup.add(types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ'))
        
        bot.send_message(chat_id, buy_text, reply_markup=back_markup)
        
    elif message.text == '💰 መሸጥ':
        # መሸጥ ሲል ብቻ የካቴጎሪ ምርጫዎች ይመጣሉ
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            types.KeyboardButton('🏠 ቤት'),
            types.KeyboardButton('🚗 መኪና'),
            types.KeyboardButton('📦 ሌሎች ነገሮች'),
            types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ')
        )
        bot.send_message(chat_id, "📋 እንዲታተም የፈለጉት ነገር ምንድን ነው?\nእባክዎ ከታች ካሉት አማራጮች አንዱን ይምረጡ።", reply_markup=markup)

# --- ወደ ዋና ማውጫ ለመመለስ ሲጫን ---
@bot.message_handler(func=lambda message: message.text == '↩️ ወደ ዋና ማውጫ ተመለስ')
def go_back_to_main(message):
    send_welcome(message)

# --- 3ኛ ደረጃ፦ ካቴጎሪ ሲመረጥ ወደ መረጃ ማስገቢያ መውሰጃ ---
@bot.message_handler(func=lambda message: message.text in ['🏠 ቤት', '🚗 መኪና', '📦 ሌሎች ነገሮች'])
def handle_category(message):
    chat_id = message.chat.id
    category = message.text
    user_sessions[chat_id] = {'category': category, 'photos': []} # ዳታ ማደራጃ
    
    remove_keyboard = types.ReplyKeyboardRemove()
    
    if category == '🏠 ቤት':
        msg = bot.send_message(chat_id, "እባኮትን የቤቱ 3 የተለያየ ፎቶ አንድ ላይ ወይም በየተራ ይላኩ (ሲጨርሱ ፎቶዎቹ በራሳቸው ይመዘገባሉ)", reply_markup=remove_keyboard)
        bot.register_next_step_handler(msg, get_house_photos)
    elif category == '🚗 መኪና':
        bot.send_message(chat_id, "የመኪና መመዝገቢያ ክፍል በቅርቡ ይለቀቃል!", reply_markup=remove_keyboard)
    elif category == '📦 ሌሎች ነገሮች':
        bot.send_message(chat_id, "የሌሎች እቃዎች መመዝገቢያ ክፍል በቅርቡ ይለቀቃል!", reply_markup=remove_keyboard)

# ==================== 🏠 የቤት ፍሰት (HOUSE FLOW) ====================
def get_house_photos(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        user_sessions[chat_id]['photos'].append(photo_id)
        
        if len(user_sessions[chat_id]['photos']) < 3:
            msg = bot.send_message(chat_id, f"በጣም ጥሩ! የቀሩ ፎቶዎች፡ {3 - len(user_sessions[chat_id]['photos'])}። እባክዎ ይላኩ...")
            bot.register_next_step_handler(msg, get_house_photos)
            return
        
        msg = bot.send_message(chat_id, "በጣም ጥሩ👌\nአሁን ደግሞ ቤቱ ባለ ስንት መኝታ ክፍል ቤት እንዳለው በቁጥር ብቻ ይግለፁ")
        bot.register_next_step_handler(msg, get_house_bedrooms)
    else:
        msg = bot.send_message(chat_id, "እባክዎ ፎቶ ይላኩ!")
        bot.register_next_step_handler(msg, get_house_photos)

def get_house_bedrooms(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['bedrooms'] = message.text
    msg = bot.send_message(chat_id, "በጣም ጥሩ👌\nአሁን ደግሞ የመታጠቢያ ቤት እንዳለው በቁጥር ብቻ ይግለፁ")
    bot.register_next_step_handler(msg, get_house_bathrooms)

def get_house_bathrooms(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['bathrooms'] = message.text
    msg = bot.send_message(chat_id, "በጣም ጥሩ👌\nአሁን ደግሞ የሚሸጡበትን የገንዘብ መጠን ያስገቡ")
    bot.register_next_step_handler(msg, get_house_price)

def get_house_price(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['price'] = message.text
    msg = bot.send_message(chat_id, "በጣም ጥሩ👌\nአሁን ደግሞ ቤቱ ያለበትን ከተማ/ሀገር ያስገቡ")
    bot.register_next_step_handler(msg, get_house_country)

def get_house_country(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['country'] = message.text
    msg = bot.send_message(chat_id, "በጣም ጥሩ👌\nአሁን ደግሞ ቤቱ ያለበት የሰፈር ስም ያስገቡ")
    bot.register_next_step_handler(msg, get_house_neighborhood)

def get_house_neighborhood(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['neighborhood'] = message.text
    msg = bot.send_message(chat_id, "በስተመጨረሻ\nየእርሶን ስልክ ቁጥር ያስገቡ")
    bot.register_next_step_handler(msg, finish_house_reg)

def finish_house_reg(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['phone'] = message.text
    user_sessions[chat_id]['username'] = message.from_user.username if message.from_user.username else "የለውም"
    
    data = user_sessions[chat_id]
    summary_text = (
        f"🏠 ቤት\n\n"
        f"መኝታ ክፍል :- {data['bedrooms']}\n"
        f"መታጠብያ ቤት :- {data['bathrooms']}\n"
        f"የገንዘብ መጠን :- {data['price']}\n"
        f"ሀገር :- {data['country']}\n"
        f"ሰፈር :- {data['neighborhood']}\n"
        f"ስልክ ቁጥር :- {data['phone']}\n"
        f"from @{data['username']} username\n"
    )
    
    media = [types.InputMediaPhoto(data['photos'][0], caption=summary_text)]
    for p_id in data['photos'][1:]:
        media.append(types.InputMediaPhoto(p_id))
        
    bot.send_media_group(chat_id, media)
    bot.send_message(chat_id, "መረጃዎት ተጣርቶ ከ Afro delala መስሪያ ቤት መልእክት ይደርሶታል\nእናመሰግናለን")

# =====================================================================
# 4. ቦቱን ማነሳሻ መጨረሻ መስመሮች (START BOT)
# =====================================================================
if __name__ == "__main__":
    keep_alive()
    print("ቦቱ መስራት ጀምሯል...")
    bot.infinity_polling()
