import os
import logging
import asyncio
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode
import json

# ሎግ ማድረግ ያብሩ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ከአንቀላፋ ፍሰት ሽፋን
import nest_asyncio
nest_asyncio.apply()

# ቦት ቶከን - ከአንቀላፋ ፍሰት አስገባ
TOKEN = os.environ.get('TOKEN') or "YOUR_BOT_TOKEN_HERE"

# ቀላል ጌም ውሂብ
SCENES = [
    {"id": 1, "title": "መጀመሪያ መገናኘት", "desc": "ዳንኤል እና ጀሚላ በዩኒቨርሲቲ ተገናኙ።", "emoji": "👫"},
    {"id": 2, "title": "የመጀመሪያ ውይይት", "desc": "በካፌቴሪያ ውስጥ ተነጋገሩ።", "emoji": "💬"},
    {"id": 3, "title": "የመጀመሪያ ቀን", "desc": "ከዩኒቨርሲቲ ውጭ ተገናኝተው ኮፊ ጠጡ።", "emoji": "☕"},
    {"id": 4, "title": "ፍቅር መጀመር", "desc": "እርስ በርስ የሚወዱበት ጊዜ ደርሷል።", "emoji": "❤️"},
    {"id": 5, "title": "በቤት ውስጥ ያለው ጊዜ", "desc": "በቤት ውስጥ አብረው የሚሳለጉበት ጊዜ።", "emoji": "🏠"},
    {"id": 6, "title": "የባህር ጉዞ", "desc": "አብረው ባህር ሄደው በውኃ ዳርቻ ጊዜ ያሳልፋሉ።", "emoji": "🌊"},
]

ACTIVITIES = [
    {"id": "similar", "name": "የመሳሰሉ ነገሮች", "emoji": "✨"},
    {"id": "tease", "name": "የመተቃቀፍ", "emoji": "😄"},
    {"id": "sleep", "name": "የመተኛት", "emoji": "😴"},
    {"id": "tv", "name": "ቴሌቭዥን ማየት", "emoji": "📺"},
    {"id": "cook", "name": "ምግብ ማብሰል", "emoji": "🍳"},
    {"id": "work", "name": "ስራ መስራት", "emoji": "💼"},
    {"id": "play_home", "name": "በቤት ውስጥ መጫወት", "emoji": "🏠"},
    {"id": "play_park", "name": "በመዝናኛ ቦታ መጫወት", "emoji": "🎡"},
    {"id": "play_beach", "name": "በባህር ዳርቻ መጫወት", "emoji": "🏖️"},
]

# ተጠቃሚ ውሂብ ማከማቻ
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የመጀመሪያ ትዕዛዝ"""
    user = update.effective_user
    user_id = user.id
    
    # ተጠቃሚ ውሂብ አስጀምር
    user_data[user_id] = {
        "name": user.first_name,
        "scene": 0,
        "score": 0,
        "activities": []
    }
    
    keyboard = [
        ["🎮 ጌም ጀምር", "📖 ታሪክ ቀጥል"],
        ["🌟 እንቅስቃሴዎች", "📊 እድገቴ"],
        ["ℹ️ ስለ ጌሙ", "❓ እርዳታ"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 ሰላም {user.first_name}!\n\n"
        "🎮 *ዳንኤል እና ጀሚላ የፍቅር ጌም* ወደ እርስዎ ተመልሷል!\n\n"
        "ይህ ጌም የሁለት ወጣቶች ፍቅር ታሪክ እንዴት እንደተሰራ ያሳያል።\n\n"
        "ለመጀመር ከታች ያሉትን ቁልፎች ይጠቀሙ!",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ጌም ለመጀመር"""
    user_id = update.effective_user.id
    
    if user_id in user_data:
        user_data[user_id]["scene"] = 0
        user_data[user_id]["score"] = 0
        user_data[user_id]["activities"] = []
    
    await update.message.reply_text(
        "🎮 *ጌም ተጀምሯል!*\n\n"
        "ዳንኤል እና ጀሚላ የፍቅር ታሪክ አሁን ይጀምራል...\n\n"
        "የመጀመሪያውን ታሪክ ለማየት '📖 ታሪክ ቀጥል' ይጫኑ።",
        parse_mode=ParseMode.MARKDOWN
    )

async def continue_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ታሪክ ለመቀጠል"""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("እባክዎ በመጀመሪያ /start ይጫኑ")
        return
    
    user = user_data[user_id]
    scene_index = user["scene"]
    
    if scene_index >= len(SCENES):
        await update.message.reply_text(
            "🎉 *ታሪኩ ተጠናቋል!*\n\n"
            "ዳንኤል እና ጀሚላ ፍቅራቸው በደስታ ቀጠለ! 🎉\n\n"
            "እንቅስቃሴዎችን ለመሞከር '🌟 እንቅስቃሴዎች' ይጫኑ።",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    scene = SCENES[scene_index]
    
    message = f"""
{scene['emoji']} *{scene['title']}*

{scene['desc']}

📊 ደረጃ: {scene_index + 1}/{len(SCENES)}
⭐ ነጥቦች: {user['score']}
"""
    
    keyboard = []
    if scene_index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ ወደ ኋላ", callback_data=f"prev_{scene_index}")])
    
    if scene_index < len(SCENES) - 1:
        keyboard.append([InlineKeyboardButton("ቀጣይ ታሪክ ➡️", callback_data=f"next_{scene_index}")])
    else:
        keyboard.append([InlineKeyboardButton("🎉 ጨርስ", callback_data="finish")])
    
    keyboard.append([InlineKeyboardButton("🌟 እንቅስቃሴ ለመስራት", callback_data="activities")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def show_activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """እንቅስቃሴዎችን ለማሳየት"""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("እባክዎ በመጀመሪያ /start ይጫኑ")
        return
    
    user = user_data[user_id]
    
    message = "🌟 *የዳንኤል እና ጀሚላ እንቅስቃሴዎች*\n\n"
    message += "ለእያንዳንዱ እንቅስቃሴ 10 ነጥቦችን ያግኙ!\n\n"
    
    keyboard = []
    row = []
    
    for i, activity in enumerate(ACTIVITIES):
        completed = "✅" if activity["id"] in user["activities"] else "🔓"
        row.append(InlineKeyboardButton(
            f"{completed} {activity['emoji']}",
            callback_data=f"act_{activity['id']}"
        ))
        
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 ወደ ዋና ገጽ", callback_data="home")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የቁልፍ ጠቅታዎችን ለማስተናገድ"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if user_id not in user_data:
        await query.edit_message_text("እባክዎ በመጀመሪያ /start ይጫኑ")
        return
    
    user = user_data[user_id]
    
    if data.startswith("next_"):
        scene_index = int(data.split("_")[1])
        user["scene"] = scene_index + 1
        user["score"] += 5  # ለታሪክ መቀጠል 5 ነጥብ
        
        scene = SCENES[user["scene"]]
        message = f"""
{scene['emoji']} *{scene['title']}*

{scene['desc']}

📊 ደረጃ: {user['scene'] + 1}/{len(SCENES)}
⭐ ነጥቦች: {user['score']} (+5 ነጥቦች!)
"""
        
        keyboard = []
        if user["scene"] > 0:
            keyboard.append([InlineKeyboardButton("⬅️ ወደ ኋላ", callback_data=f"prev_{user['scene']}")])
        
        if user["scene"] < len(SCENES) - 1:
            keyboard.append([InlineKeyboardButton("ቀጣይ ታሪክ ➡️", callback_data=f"next_{user['scene']}")])
        else:
            keyboard.append([InlineKeyboardButton("🎉 ጨርስ", callback_data="finish")])
        
        keyboard.append([InlineKeyboardButton("🌟 እንቅስቃሴ ለመስራት", callback_data="activities")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("prev_"):
        scene_index = int(data.split("_")[1])
        user["scene"] = scene_index - 1
        
        scene = SCENES[user["scene"]]
        message = f"""
{scene['emoji']} *{scene['title']}*

{scene['desc']}

📊 ደረጃ: {user['scene'] + 1}/{len(SCENES)}
⭐ ነጥቦች: {user['score']}
"""
        
        keyboard = []
        if user["scene"] > 0:
            keyboard.append([InlineKeyboardButton("⬅️ ወደ ኋላ", callback_data=f"prev_{user['scene']}")])
        
        if user["scene"] < len(SCENES) - 1:
            keyboard.append([InlineKeyboardButton("ቀጣይ ታሪክ ➡️", callback_data=f"next_{user['scene']}")])
        else:
            keyboard.append([InlineKeyboardButton("🎉 ጨርስ", callback_data="finish")])
        
        keyboard.append([InlineKeyboardButton("🌟 እንቅስቃሴ ለመስራት", callback_data="activities")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("act_"):
        activity_id = data.split("_")[1]
        activity = next((a for a in ACTIVITIES if a["id"] == activity_id), None)
        
        if activity:
            if activity_id not in user["activities"]:
                user["activities"].append(activity_id)
                user["score"] += 10  # ለእንቅስቃሴ መጨረስ 10 ነጥብ
                
                message = f"""
🎉 *በጣም ግሩም!*

{activity['emoji']} *{activity['name']}* አጠናቀህ!

✅ እንቅስቃሴውን አጠናቀሃል!
⭐ +10 ነጥቦች ተጨምረዋል!
💰 አጠቃላይ ነጥቦች: {user['score']}

ተጨማሪ ነጥቦች ለማግኘት ሌሎች እንቅስቃሴዎችን ሞክር!
"""
            else:
                message = f"""
✅ *አስቀምጠሃል!*

{activity['emoji']} *{activity['name']}* ከዚህ በፊት አጠናቅሀዋል!

💰 አጠቃላይ ነጥቦች: {user['score']}
"""
            
            keyboard = [
                [InlineKeyboardButton("🌟 ተጨማሪ እንቅስቃሴዎች", callback_data="activities")],
                [InlineKeyboardButton("📖 ታሪክ ቀጥል", callback_data=f"next_{user['scene']}")],
                [InlineKeyboardButton("🏠 ወደ ዋና ገጽ", callback_data="home")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif data == "activities":
        await show_activities_callback(query)
    
    elif data == "home":
        keyboard = [
            ["🎮 ጌም ጀምር", "📖 ታሪክ ቀጥል"],
            ["🌟 እንቅስቃሴዎች", "📊 እድገቴ"],
            ["ℹ️ ስለ ጌሙ", "❓ እርዳታ"]
        ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await query.edit_message_text(
            "🏠 *ዋና ገጽ*\n\nከታች ያሉትን ቁልፎች ይጠቀሙ።",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "finish":
        message = f"""
🎉 *ታሪኩ ተጠናቋል!*

ዳንኤል እና ጀሚላ ፍቅራቸው በደስታ ቀጠለ! 🎉

📊 *የእርስዎ ውጤት:*
⭐ አጠቃላይ ነጥቦች: {user['score']}
✅ የተጠናቀቁ እንቅስቃሴዎች: {len(user['activities'])}/{len(ACTIVITIES)}
📖 የተጠናቀቁ ታሪኮች: {user['scene'] + 1}/{len(SCENES)}

እንኳን ደስ አለህ! 🏆
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 እንደገና ጀምር", callback_data="restart")],
            [InlineKeyboardButton("🌟 እንቅስቃሴዎች", callback_data="activities")],
            [InlineKeyboardButton("🏠 ወደ ዋና ገጽ", callback_data="home")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "restart":
        user["scene"] = 0
        user["score"] = 0
        user["activities"] = []
        
        await query.edit_message_text(
            "🔄 *ጌም እንደገና ተጀምሯል!*\n\n"
            "ሁሉም ነገር ወደ መጀመሪያ ተመለሰ!\n\n"
            "ለመጀመር '📖 ታሪክ ቀጥል' ይጫኑ።",
            parse_mode=ParseMode.MARKDOWN
        )

async def show_activities_callback(query):
    """እንቅስቃሴዎችን ለማሳየት (ለ callback)"""
    user_id = query.from_user.id
    
    if user_id not in user_data:
        await query.edit_message_text("እባክዎ በመጀመሪያ /start ይጫኑ")
        return
    
    user = user_data[user_id]
    
    message = "🌟 *የዳንኤል እና ጀሚላ እንቅስቃሴዎች*\n\n"
    message += "ለእያንዳንዱ እንቅስቃሴ 10 ነጥቦችን ያግኙ!\n\n"
    
    keyboard = []
    row = []
    
    for i, activity in enumerate(ACTIVITIES):
        completed = "✅" if activity["id"] in user["activities"] else "🔓"
        row.append(InlineKeyboardButton(
            f"{completed} {activity['emoji']}",
            callback_data=f"act_{activity['id']}"
        ))
        
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 ወደ ዋና ገጽ", callback_data="home")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የተጠቃሚ እድገት ለማሳየት"""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("እባክዎ በመጀመሪያ /start ይጫኑ")
        return
    
    user = user_data[user_id]
    
    message = f"""
📊 *የእርስዎ እድገት*

👤 ተጫዋች: {user['name']}
⭐ አጠቃላይ ነጥቦች: {user['score']}

📖 *የታሪክ እድገት:*
{user['scene'] + 1}/{len(SCENES)} ታሪኮች

🌟 *የእንቅስቃሴ እድገት:*
{len(user['activities'])}/{len(ACTIVITIES)} እንቅስቃሴዎች

🔓 *የተከፈቱ ነገሮች:*
"""
    
    if len(user["activities"]) > 0:
        for activity_id in user["activities"]:
            activity = next((a for a in ACTIVITIES if a["id"] == activity_id), None)
            if activity:
                message += f"✅ {activity['emoji']} {activity['name']}\n"
    else:
        message += "ምንም እንቅስቃሴ አልተጠናቀቀም። ለመጀመር '🌟 እንቅስቃሴዎች' ይጫኑ!\n"
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )

async def about_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ስለ ጌሙ መረጃ"""
    message = """
*ዳንኤል እና ጀሚላ የፍቅር ጌም*

🎮 *ስለ ጌሙ:*
ይህ ጌም የሁለት ወጣቶች ፍቅር ታሪክ እንዴት እንደተሰራ ያሳያል። 
በተለያዩ እንቅስቃሴዎች እና በህይወታቸው ውስጥ ያሉ የዕለት ተዕለት ነገሮች በኩል።

🌟 *ዋና እንቅስቃሴዎች:*
• የመሳሰሉ ነገሮችን ማግኘት
• በፍቅር መተቃቀቅ
• አብረው መተኛት
• ቴሌቭዥን ማየት
• ምግብ ማብሰል
• ስራ መስራት
• በተለያዩ ቦታዎች መጫወት

🎯 *ግብ:*
• ሁሉንም ታሪኮች አጥንተህ ማሳየት
• ሁሉንም እንቅስቃሴዎች ማጠናቀቅ
• ብዙ ነጥቦች ማግኘት

👨‍💻 *አበልፃጊ:* በPython ተገንብቷል
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """እርዳታ ትዕዛዝ"""
    message = """
*❓ እርዳታ እና መመሪያዎች*

🎮 *ጌም እንዴት ይጫወታል:*
1. '🎮 ጌም ጀምር' በማለት ጀምር
2. ታሪኩን ለመከተል '📖 ታሪክ ቀጥል' ይጫኑ
3. ነጥቦች ለማግኘት '🌟 እንቅስቃሴዎች' ይጫኑ
4. እያንዳንዱን እንቅስቃሴ በመጨረስ ነጥቦችን ያግኙ

🌟 *እንቅስቃሴዎች:*
• እያንዳንዱ እንቅስቃሴ 10 ነጥቦችን ይሰጣል
• ሁሉንም እንቅስቃሴዎች ለማጠናቀቅ ይሞክሩ

📊 *እድገት:*
• '📊 እድገቴ' በማለት እድገትዎን ይመልከቱ

🔧 *ትዕዛዞች:*
/start - ጌም ለመጀመር
/help - ይህን መልዕክት ለማሳየት

🎉 *ደስተኛ ጨዋታ!*
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """መልዕክቶችን ለማስተናገድ"""
    text = update.message.text
    
    if text == "🎮 ጌም ጀምር":
        await start_game(update, context)
    elif text == "📖 ታሪክ ቀጥል":
        await continue_story(update, context)
    elif text == "🌟 እንቅስቃሴዎች":
        await show_activities(update, context)
    elif text == "📊 እድገቴ":
        await show_progress(update, context)
    elif text == "ℹ️ ስለ ጌሙ":
        await about_game(update, context)
    elif text == "❓ እርዳታ":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "እባክዎ ከታች ያሉትን ቁልፎች ይጠቀሙ።",
            parse_mode=ParseMode.MARKDOWN
        )

def main():
    """ዋና ተግባር"""
    # ቦት አተገባበር ይፍጠሩ
    application = Application.builder().token(TOKEN).build()
    
    # ትዕዛዞችን ያክሉ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # የቁልፍ ጠቅታዎችን ያክሉ
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # መልዕክቶችን ያክሉ
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # ቦትን ያስኬዱ
    print("🤖 ቦቱ በReplit ላይ እየሰራ ነው...")
    print("📱 Telegram ውስጥ ቦትዎን ይክፈቱ እና /start ይጻፉ")
    
    # Polling ይጀምሩ
    application.run_polling()

if __name__ == "__main__":
    main()
