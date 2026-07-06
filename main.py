import telebot
from telebot import types
import os
from threading import Thread
from flask import Flask

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

API_TOKEN = '8709684996:AAEJOSnQZehV6T9ED2lP6HXeKVY5QJ9C-OQ'
bot = telebot.TeleBot(API_TOKEN)

# የድሮውን ዌብሁክ ለማጥፋት ይህንን ይጨምሩ
bot.delete_webhook()

# የተጠቃሚዎችን መረጃ ጊዜያዊ ማከማቻ
user_sessions = {}

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {} # ሰsession መክፈት
    
    welcome_text = (
        "📢 ማስታወሻ\n\n"
        "እንኳን ወደ Afro Delala Bot በደህና መጡ!\n\n"
        "- በ Afro Delala ድረ-ገጽ ላይ ያስገቡት መረጃ እንዲታተም እና እንዲለቀቅ 20 ብር የአገልግሎት ክፍያ ያስፈልጋል።\n"
        "- እባኮትን የሚጠየቁትን መረጃ በስነስርአት ለማስገባት ይሞክሩ። የተጠየቁት መረጃ እና መልሶ ካልተመሳሰለ የማተሙ ሂደት ውድቅ ይሆናል።\n\n"
        "እባክዎ ይህን መረጃ በጥንቃቄ ካነበቡ በኋላ \"ቀጥል\" የሚለውን ቁልፍ ይጫኑ ወይም \"ቀጥል\" ብለው ይላኩ።"
    )
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('ቀጥል'))
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

# --- ቀጥል ሲል ---
@bot.message_handler(func=lambda message: message.text == "ቀጥል")
def choose_category(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('🏠 ቤት'),
        types.KeyboardButton('🚗 መኪና'),
        types.KeyboardButton('📦 ሌሎች ነገሮች')
    )
    bot.send_message(chat_id, "📋 እንዲታተም የፈለጉት ነገር ምንድን ነው?\nእባክዎ ከታች ካሉት አማራጮች አንዱን ይምረጡ።", reply_markup=markup)

# --- ካቴጎሪ መረጣ ---
@bot.message_handler(func=lambda message: message.text in ['🏠 ቤት', '🚗 መኪና', '📦 ሌሎች ነገሮች'])
def handle_category(message):
    chat_id = message.chat.id
    category = message.text
    user_sessions[chat_id] = {'category': category, 'photos': []} # ዳታ ማደራጃ
    
    # የቁልፍ ሰሌዳውን ማጥፊያ
    remove_keyboard = types.ReplyKeyboardRemove()
    
    if category == '🏠 ቤት':
        msg = bot.send_message(chat_id, "እባኮትን የቤቱ 3 የተለያየ ፎቶ አንድ ላይ ወይም በየተራ ይላኩ (ሲጨርሱ ፎቶዎቹ በራሳቸው ይመዘገባሉ)", reply_markup=remove_keyboard)
        bot.register_next_step_handler(msg, get_house_photos)
    elif category == '🚗 መኪና':
        msg = bot.send_message(chat_id, "እባኮትን የመኪናውን ስም ያስገቡ", reply_markup=remove_keyboard)
        bot.register_next_step_handler(msg, get_car_name)
    elif category == '📦 ሌሎች ነገሮች':
        msg = bot.send_message(chat_id, "እባኮትን የእቃውን ስም ያስገቡ", reply_markup=remove_keyboard)
        bot.register_next_step_handler(msg, get_thing_name)

# ==================== 🏠 የቤት ፍሰት (HOUSE FLOW) ====================
def get_house_photos(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        # የፎቶውን ID መያዝ
        photo_id = message.photo[-1].file_id
        user_sessions[chat_id]['photos'].append(photo_id)
        
        # 3 ፎቶ እስኪሞላ መጠበቅ
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
    
    # አንተ በፈለግኸው ስታይል ፅሁፉን ማቀናጀት
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
    
    # ፎቶዎቹን በአንድ ላይ (Media Group) አድርጎ መላክ
    media = [types.InputMediaPhoto(data['photos'][0], caption=summary_text)]
    for p_id in data['photos'][1:]:
        media.append(types.InputMediaPhoto(p_id))
        
    # ማስታወሻ፡ እዚህ ጋር ወደ ራስህ አካውንት ወይም ግሩፕ እንዲልክ ማድረግ ትችላለህ (ለምሳሌ ለጊዜው ለራሱ ለተጠቃሚው ይላከው)
    bot.send_media_group(chat_id, media)
    
    bot.send_message(chat_id, "መረጃዎት ተጣርቶ ከ Afro delala መስሪያ ቤት መልእክት ይደርሶታል\nእናመሰግናለን")

# =====================================================================
# ማስታወሻ፡ የ🚗 መኪና እና የ📦 ሌሎች ነገሮች ፍሰትም ልክ እንደዚሁ በተመሳሳይ መልክ ይቀጥላል።

bot.infinity_polling()
# ... ያንተ የቀደመው ኮድ እዚህ ያበቃል ...

keep_alive()  # ይህ አዲስ የሚጨመረው ነው
print("ቦቱ መስራት ጀምሯል...")
bot.infinity_polling() # ያንተ የነበረው መጨረሻ መስመር
