from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData

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
    [InlineKeyboardButton(text="➡️ Skip", callback_data="skip_rating")]
]
rating_menu = InlineKeyboardMarkup(inline_keyboard=rating_menu)


class booking_button_callback(CallbackData, prefix="booking"):
    action: int
    date: int
    hour: str
def new_cb(action=1, date=0, hour=""):
    return booking_button_callback(action=action, date=date, hour=hour).pack()


calendar_start_menu = [
    [InlineKeyboardButton(text="🔝 Get Started", callback_data=new_cb(action=0))],
    [InlineKeyboardButton(text="➡️ Skip", callback_data="skip_booking")]
]
calendar_start_menu = InlineKeyboardMarkup(inline_keyboard=calendar_start_menu)

finish_button = [
    [InlineKeyboardButton(text="🚀 Let's Go", callback_data="to_db")]
]
finish_button = InlineKeyboardMarkup(inline_keyboard=finish_button)

async def calendar_kb(cur_date, date):
    markup = []
    for hours in cur_date:
        row=[]
        row.append(InlineKeyboardButton(text=str(hours), callback_data="help"))
        if cur_date[hours]:
            row.append(InlineKeyboardButton(text="✅", callback_data=new_cb(date=date, hour=str(hours))))
        else:
            row.append(InlineKeyboardButton(text="⚪️", callback_data=new_cb(date=date, hour=str(hours))))
        markup.append(row)
    submit = [(InlineKeyboardButton(text="✅Submit and go to next", 
                                    callback_data=new_cb(action=2)))]
    markup.append(submit)
    return InlineKeyboardMarkup(inline_keyboard=markup)
