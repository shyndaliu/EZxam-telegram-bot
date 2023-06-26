from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
menu = [
    [InlineKeyboardButton(text="📝 Chat with Cal Newport", callback_data="generate_text"),
     InlineKeyboardButton(text="🖼 Open tables menu", callback_data="table_menu")],
    [InlineKeyboardButton(text="🔎 Help", callback_data="help")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Back to menu")]], resize_keyboard=True)

table_menu = [
    [InlineKeyboardButton(text="📋 My tables", callback_data="get_tables"),
     InlineKeyboardButton(text="📆 Create new table", callback_data="generate_table")],
    [InlineKeyboardButton(text="🔎 Help", callback_data="help")]
]
table_menu = InlineKeyboardMarkup(inline_keyboard=table_menu)

enter_deadline = [
    [InlineKeyboardButton(text="Enter again", callback_data="enter_deadline")]
]
enter_deadline = InlineKeyboardMarkup(inline_keyboard=enter_deadline)

rating_menu = [
    [InlineKeyboardButton(text="⭐️ Start rating", callback_data="help"),
     InlineKeyboardButton(text="➡️ Skip", callback_data="help")]
]
rating_menu = InlineKeyboardMarkup(inline_keyboard=rating_menu)