import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# =====================================================================
# 1. FLASK ሰርቨር (Render Port Binding)
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
# 2. የቦቱ ዋና ቅንብር
# =====================================================================
API_TOKEN = '8709684996:AAEJOSnQZehV6T9ED2lP6HXeKVY5QJ9C-OQ'
MY_TELEGRAM_ID = 'ያንተን_ID_እዚህ_አስገባ' # 👈 የራስህን የቴሌግራም ID እዚህ ማስገባትህን እንዳትረሳ!
bot = telebot.TeleBot(API_TOKEN)

bot.delete_webhook()
user_sessions = {}

# =====================================================================
# 3. የባንክ መረጃ ማስተካከያ (መረጃው ሲጸድቅ ለተጠቃሚው የሚላክ)
# =====================================================================
BANK_INFO = (
    "\n\n💳 የክፍያ አማራጮች (Afro Delala)\n"
    "መረጃዎ በቻናላችን ላይ እንዲፖሰት እባክዎ ክፍያ ይፈጽሙ፦\n\n"
    "📌 የባንክ ስም: የኢትዮጵያ ንግድ ባንክ (CBE)\n"
    "📌 የሂሳብ ቁጥር: 1000XXXXXXXXX\n"
    "📌 የሂሳብ ስም: [ያንተ ስም]\n\n"
    "💵 ክፍያውን ከፈጸሙ በኋላ የደረሰኝ (Receipt) ፎቶ ወይም ስክሪንሹት እዚህ ይላኩ።"
)

# =====================================================================
# 4. የቦቱ ማጽደቂያ ቁልፎች ፈጠራ (Inline Buttons)
# =====================================================================
def get_approval_keyboard(user_id, category):
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ ጽድቋል", callback_data=f"approve_{user_id}_{category}")
    reject_btn = types.InlineKeyboardButton("❌ ውድቅ ሆኗል", callback_data=f"reject_{user_id}_{category}")
    markup.add(approve_btn, reject_btn)
    return markup

# =====================================================================
# 5. የቦቱ ዋና ፍሰቶች
# =====================================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {}
    welcome_text = "መጀመሪያ እንኳን በሰላም መጡ! በዚህ ቦት ላይ ምን ማድረግ ነው የፈለጉት?"
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('🛒 መግዛት'), types.KeyboardButton('💰 መሸጥ'))
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['🛒 መግዛት', '💰 መሸጥ', '↩️ ወደ ዋና ማውጫ ተመለስ'])
def handle_buy_sell(message):
    chat_id = message.chat.id
    if message.text == '↩️ ወደ ዋና ማውጫ ተመለስ':
        send_welcome(message)
    elif message.text == '🛒 መግዛት':
        bot.send_message(chat_id, "እዚህ ላይ የዌብሳይት እና የቴሌግራም ሊንኮችህን አስገባ", reply_markup=types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ')))
    elif message.text == '💰 መሸጥ':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(types.KeyboardButton('🏠 ቤት'), types.KeyboardButton('🚗 መኪና'), types.KeyboardButton('📦 ሌሎች ነገሮች'))
        bot.send_message(chat_id, "ምን ለመሸጥ ፈልገዋል?", reply_markup=markup)

# --- የባንክ ደረሰኝ መቀበያ ፍሰት ---
def handle_bank_receipt(message):
    chat_id = message.chat.id
    if message.text == '↩️ ወደ ዋና ማውጫ ተመለስ':
        send_welcome(message)
        return
    if message.content_type == 'photo':
        bot.send_message(chat_id, "የከፈሉበት ደረሰኝ ደርሶናል! መረጃው ተጣርቶ በቅርቡ እናሳውቆታለን። እናመሰግናለን።")
        # ደረሰኙን በቀጥታ ለአንተ ይልካል
        bot.send_photo(MY_TELEGRAM_ID, message.photo[-1].file_id, caption=f"💰 አዲስ የባንክ ደረሰኝ ተልኳል!\nከ User ID: {chat_id} | @{message.from_user.username if message.from_user.username else 'የለውም'}")
    else:
        msg = bot.send_message(chat_id, "እባክዎ የባንክ ደረሰኝ ፎቶ (Screenshot) ብቻ ይላኩ ወይም '↩️ ወደ ዋና ማውጫ ተመለስ' የሚለውን ይጫኑ")
        bot.register_next_step_handler(msg, handle_bank_receipt)

@bot.message_handler(func=lambda message: message.text in ['🏠 ቤት', '🚗 መኪና', '📦 ሌሎች ነገሮች'])
def handle_category(message):
    chat_id = message.chat.id
    category = message.text
    user_sessions[chat_id] = {'category': category, 'photos': []}
    if category == '🏠 ቤት':
        msg = bot.send_message(chat_id, "የቤቱን 3 ፎቶ ይላኩ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_house_photos)
    elif category == '🚗 መኪና':
        msg = bot.send_message(chat_id, "የመኪናውን 3 ፎቶ ይላኩ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_car_photos)

# ==================== 🏠 የቤት ፍሰት (HOUSE FLOW) ====================
def get_house_photos(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        user_sessions[chat_id]['photos'].append(message.photo[-1].file_id)
        if len(user_sessions[chat_id]['photos']) < 3:
            msg = bot.send_message(chat_id, f"የቀሩ ፎቶዎች፡ {3 - len(user_sessions[chat_id]['photos'])}። እባክዎ ይላኩ...")
            bot.register_next_step_handler(msg, get_house_photos)
            return
        msg = bot.send_message(chat_id, "በጣም ጥሩ👌\nአሁን ደግሞ ቤቱ ባለ ስንት መኝታ ክፍል ቤት እንዳለው በቁጥር ብቻ ይግለፁ")
        bot.register_next_step_handler(msg, get_house_bedrooms)
    else:
        msg = bot.send_message(chat_id, "እባክዎ ፎቶ ይላኩ!")
        bot.register_next_step_handler(msg, get_house_photos)

def get_house_bedrooms(message):
    user_sessions[message.chat.id]['bedrooms'] = message.text
    msg = bot.send_message(message.chat.id, "በጣም ጥሩ👌\nአሁን ደግሞ የመታጠቢያ ቤት እንዳለው በቁጥር ብቻ ይግለፁ")
    bot.register_next_step_handler(msg, get_house_bathrooms)

def get_house_bathrooms(message):
    user_sessions[message.chat.id]['bathrooms'] = message.text
    msg = bot.send_message(message.chat.id, "በጣም ጥሩ👌\nአሁን ደግሞ የሚሸጡበትን የገንዘብ መጠን ያስገቡ")
    bot.register_next_step_handler(msg, get_house_price)

def get_house_price(message):
    user_sessions[message.chat.id]['price'] = message.text
    msg = bot.send_message(message.chat.id, "በጣም ጥሩ👌\nአሁን ደግሞ ቤቱ ያለበትን ከተማ/ሀገር ያስገቡ")
    bot.register_next_step_handler(msg, get_house_country)

def get_house_country(message):
    user_sessions[message.chat.id]['country'] = message.text
    msg = bot.send_message(message.chat.id, "በጣም ጥሩ👌\nአሁን ደግሞ ቤቱ ያለበት የሰፈር ስም ያስገቡ")
    bot.register_next_step_handler(msg, get_house_neighborhood)

def get_house_neighborhood(message):
    user_sessions[message.chat.id]['neighborhood'] = message.text
    msg = bot.send_message(message.chat.id, "በስተመጨረሻ\nየእርሶን ስልክ ቁጥር ያስገቡ")
    bot.register_next_step_handler(msg, finish_house_reg)

def finish_house_reg(message):
    chat_id = message.chat.id
    data = user_sessions[chat_id]
    data['phone'] = message.text
    data['username'] = message.from_user.username if message.from_user.username else "የለውም"
    
    summary = (
        f"🏠 አዲስ ቤት መረጃ፦\n\n"
        f"መኝታ ክፍል :- {data['bedrooms']}\n"
        f"መታጠብያ ቤት :- {data['bathrooms']}\n"
        f"የገንዘብ መጠን :- {data['price']}\n"
        f"ሀገር :- {data['country']}\n"
        f"ሰፈር :- {data['neighborhood']}\n"
        f"ስልክ ቁጥር :- {data['phone']}\n"
        f"User: @{data['username']}"
    )
    
    media = [types.InputMediaPhoto(data['photos'][0], caption=summary)]
    for p_id in data['photos'][1:]: 
        media.append(types.InputMediaPhoto(p_id))
    
    # መረጃውን እና የውሳኔ ቁልፎቹን ለአንተ መላክ
    bot.send_media_group(MY_TELEGRAM_ID, media) 
    bot.send_message(MY_TELEGRAM_ID, f"የ @{data['username']} የቤት መረጃ ላይ ምን መወሰን ይፈልጋሉ?", reply_markup=get_approval_keyboard(chat_id, "ቤት"))
    
    back_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ'))
    bot.send_message(chat_id, "መረጃዎት ተጣርቶ ከ Afro delala መስሪያ ቤት መልእክት ይደርሶታል\nእናመሰግናለን", reply_markup=back_markup)


# ==================== 🚗 የመኪና ፍሰት (CAR FLOW) ====================
def get_car_photos(message):
    if message.content_type == 'photo':
        user_sessions[message.chat.id]['photos'].append(message.photo[-1].file_id)
        if len(user_sessions[message.chat.id]['photos']) < 3:
            msg = bot.send_message(message.chat.id, "ቀጣይ ፎቶ ይላኩ...")
            bot.register_next_step_handler(msg, get_car_photos)
            return
        msg = bot.send_message(message.chat.id, "የመኪናውን ስም ያስገቡ")
        bot.register_next_step_handler(msg, get_car_name)
    else: 
        bot.register_next_step_handler(bot.send_message(message.chat.id, "ፎቶ ብቻ ይላኩ"), get_car_photos)

def get_car_name(message):
    user_sessions[message.chat.id]['car_name'] = message.text
    msg = bot.send_message(message.chat.id, "ሞዴል/ዓመተ ምህረት ያስገቡ")
    bot.register_next_step_handler(msg, get_car_model)

def get_car_model(message):
    user_sessions[message.chat.id]['model'] = message.text
    msg = bot.send_message(message.chat.id, "የገንዘብ መጠን ያስገቡ")
    bot.register_next_step_handler(msg, get_car_price)

def get_car_price(message):
    user_sessions[message.chat.id]['price'] = message.text
    msg = bot.send_message(message.chat.id, "ያለበትን ከተማ ያስገቡ")
    bot.register_next_step_handler(msg, get_car_country)

def get_car_country(message):
    user_sessions[message.chat.id]['country'] = message.text
    msg = bot.send_message(message.chat.id, "ስልክ ቁጥር ያስገቡ")
    bot.register_next_step_handler(msg, finish_car_reg)

def finish_car_reg(message):
    chat_id = message.chat.id
    data = user_sessions[chat_id]
    data['phone'] = message.text
    data['username'] = message.from_user.username if message.from_user.username else "የለውም"
    
    summary = (
        f"🚗 አዲስ መኪና መረጃ፦\n\n"
        f"ስም: {data['car_name']}\n"
        f"ሞዴል: {data['model']}\n"
        f"ዋጋ: {data['price']}\n"
        f"ከተማ: {data['country']}\n"
        f"ስልክ: {data['phone']}\n"
        f"User: @{data['username']}"
    )
    
    media = [types.InputMediaPhoto(data['photos'][0], caption=summary)]
    for p_id in data['photos'][1:]: 
        media.append(types.InputMediaPhoto(p_id))
    
    # መረጃውን እና የውሳኔ ቁልፎቹን ለአንተ መላክ
    bot.send_media_group(MY_TELEGRAM_ID, media) 
    bot.send_message(MY_TELEGRAM_ID, f"የ @{data['username']} የመኪና መረጃ ላይ ምን መወሰን ይፈልጋሉ?", reply_markup=get_approval_keyboard(chat_id, "መኪና"))
    
    back_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ'))
    bot.send_message(chat_id, "መረጃዎት ተጣርቶ ከ Afro delala መስሪያ ቤት መልእክት ይደርሶታል\nእናመሰግናለን", reply_markup=back_markup)

# =====================================================================
# 6. የቁልፎቹ ስራ (Inline Query Handler)
# =====================================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_approval(call):
    action, user_id, category = call.data.split('_')
    user_id = int(user_id)
    
    if action == 'approve':
        bot.answer_callback_query(call.id, "መረጃው ጸድቋል!")
        bot.edit_message_text(f"✅ የዚህን ተጠቃሚ ({user_id}) የ{category} መረጃ አጽድቀኸዋል። ለተጠቃሚው የባንክ መረጃ ተልኳል።", chat_id=call.message.chat.id, message_id=call.message.message_id)
        
        # 🔔 መረጃው ሲጸድቅ ለተጠቃሚው የሚላክ መልእክት (ከባንክ አማራጭ ጋር)
        approved_msg = f"🎉 እንኳን ደስ አሎት! ያቀረቡት የ{category} መረጃ በ Afro Delala ተቀባይነት አግኝቶ ጸድቋል።" + BANK_INFO
        
        msg = bot.send_message(user_id, approved_msg, reply_markup=types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ')))
        
        # ተጠቃሚው ቀጥታ ደረሰኝ እንዲልክ መድረሻውን (Handler) እንከፍታለን
        bot.register_next_step_handler(msg, handle_bank_receipt)
        
    elif action == 'reject':
        bot.answer_callback_query(call.id, "መረጃው ውድቅ ተደርጓል")
        bot.edit_message_text(f"❌ የዚህን ተጠቃሚ ({user_id}) የ{category} መረጃ ውድቅ አድርገኸዋል።", chat_id=call.message.chat.id, message_id=call.message.message_id)
        
        # ለተጠቃሚው የሚላክ መልእክት
        bot.send_message(user_id, f"⚠️ ይቅርታ偏 ያቀረቡት የ{category} መረጃ በጋይድላይናችን መሰረት ተቀባይነት ስላላገኘ ውድቅ ሆኗል። እባክዎ መረጃዎችን በትክክል አስተካክለው ድጋሚ ይሞክሩ።")

# =====================================================================
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
    chat_id = message.chat.id
    user_sessions[chat_id]['phone'] = message.text
    user_sessions[chat_id]['username'] = message.from_user.username if message.from_user.username else "የለውም"
    
    data = user_sessions[chat_id]
    summary_text = (
        f"🚗 መኪና\n\n"
        f"የመኪና ስም :- {data['car_name']}\n"
        f"ሞዴል :- {data['model']}\n"
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
    
    # ማረጋገጫው ከተነገረ በኋላ መመለሻው ቁልፍ እዚህም ይመጣል
    back_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_markup.add(types.KeyboardButton('↩️ ወደ ዋና ማውጫ ተመለስ'))
    
    bot.send_message(chat_id, "መረጃዎት ተጣርቶ ከ Afro delala መስሪያ ቤት መልእክት ይደርሶታል\nእናመሰግናለን", reply_markup=back_markup)

# =====================================================================
# 4. ቦቱን ማነሳሻ መጨረሻ መስመሮች (START BOT)
# =====================================================================
if __name__ == "__main__":
    keep_alive()
    print("ቦቱ መስራት ጀምሯል...")
    bot.infinity_polling()
