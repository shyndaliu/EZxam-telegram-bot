from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import flags
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery

from states import Gen
from states import GetInfo
from states import GenTable

from datetime import timedelta, date, datetime
import re
import json
import time

import utils
import keyboards
import text
import db
from keyboards import booking_button_callback 

router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await db.add_user(msg.from_user.id)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=keyboards.menu)


@router.callback_query(F.data == "help")
async def help_handler(clbck: CallbackQuery, state: FSMContext):
    await state.clear()
    await clbck.message.answer(text.help_list)

@router.message(Command("help"))
async def help_handler2(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(text.help_list)


@router.message(Command("menu"))
async def menu_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(text.menu, reply_markup=keyboards.menu)


@router.message(Command("my_balance"))
async def my_balance_handler(msg: Message):
    cur_balance = await db.get_balance(msg.from_user.id)
    await msg.answer("Your current balance is: {} tokens".format(cur_balance))


@router.message(F.text == "◀️ Back to menu")
async def menu(msg: Message, state:FSMContext):
    await state.clear()
    await msg.answer(text.menu, reply_markup=keyboards.menu)


#CHAT FUNCTIONS - TEXT GENERATION
@router.callback_query(F.data == "generate_text")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_prompt)
    await clbck.message.answer(text.gen_text, reply_markup=keyboards.exit_kb)


@router.message(Gen.text_prompt)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    check = await db.check_balance(msg.from_user.id)
    if not check:
        state.clear()
        return await msg.answer(text.balance_error, reply_markup=keyboards.exit_kb)

    context = await db.get_request_response(msg.from_user.id)
    prompt = text.prompt_chat.format(prev_request=context[0], prev_response=context[1], message=msg.text)

    res = await utils.generate_text(prompt)
    if not res:
        state.clear()
        return await msg.answer(text.gen_error, reply_markup=keyboards.exit_kb)

    await db.update_request_response(msg.from_user.id, msg.text, res[0])
    await msg.answer(res[0], disable_web_page_preview=True, reply_markup=keyboards.exit_kb)
    await db.update_balance(msg.from_user.id, res[1])


#TABLE menu

@router.callback_query(F.data == "table_menu")
async def table_menu(clbck: CallbackQuery):
    await clbck.message.answer(
        "Welcome to tables menu, here you can see your tables and create new one", 
        reply_markup=keyboards.table_menu)

@router.callback_query(F.data == "get_tables")
async def my_tables(clbck: CallbackQuery):
    tables = await db.get_tables(clbck.from_user.id)
    if len(tables)==0:
        return await clbck.message.answer("You don't have any table yet", 
        reply_markup=keyboards.exit_kb)
    await clbck.message.answer("*here could be your tables", 
        reply_markup=keyboards.exit_kb)

#TABLE GENERATION--------------------------------------------------------------   

@router.callback_query(F.data == "generate_table")
async def input_table_first(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(GetInfo.get_deadline)
    await clbck.message.answer(text.table_text, reply_markup=keyboards.exit_kb)
    await clbck.message.answer("Enter the date [DD.MM.YY HH:MM] of the <em>day X</em>\nex. 05.03", reply_markup=keyboards.exit_kb)

@router.message(GetInfo.get_deadline)
@flags.chat_action("typing")
async def input_table_deadline(msg: Message, state: FSMContext):
    check = await db.check_balance(msg.from_user.id)
    if not check:
        state.clear()
        return await msg.answer(text.balance_error, reply_markup=keyboards.exit_kb)
    
    check_date = await utils.check_smth(text.check_date_prompt.format(input=msg.text, year=date.today().year))
    if not check_date:
        return await msg.answer(text.err, 
                                reply_markup=keyboards.exit_kb)

    await db.update_balance(msg.from_user.id, check_date[1])
    check_date = check_date[0]

    if check_date[0:2] != "OK":
        return await msg.answer("Invalid data or format, try again", 
                                reply_markup=keyboards.exit_kb)

    now = datetime.now() 
    given = datetime.now()
    try:
        given = datetime.strptime(check_date[4:], '%d.%m.%Y %H:%M')
    except ValueError:
        given = datetime.strptime(check_date[4:], '%d.%m.%y %H:%M')

    if given < now + timedelta(hours=1):
        return await msg.answer("Wow, isn't it too soon?...", 
                                reply_markup=keyboards.exit_kb)

    await msg.answer(f"You've entered this date: {check_date[3:]}")
    await state.update_data(deadline=check_date[3:])

    await msg.answer(text.get_topics, 
                     reply_markup=keyboards.exit_kb)
    await state.set_state(GetInfo.get_topics)


@router.message(GetInfo.get_topics)
@flags.chat_action("typing")
async def input_table_topics(msg: Message, state: FSMContext):
    check = await db.check_balance(msg.from_user.id)
    if not check:
        state.clear()
        return await msg.answer(text.balance_error, reply_markup=keyboards.exit_kb)

    check_topics = await utils.check_smth(text.check_topics_prompt.format(input=msg.text))
    if not check_topics:
        return await msg.answer(text.err, 
                                reply_markup=keyboards.exit_kb)

    await db.update_balance(msg.from_user.id, check_topics[1])
    check_topics = check_topics[0]

    if "error" in check_topics.lower():
        return await msg.answer("Something went wrong, try again", 
                                reply_markup=keyboards.exit_kb)

    await msg.answer(f"You've entered these topics: " + check_topics)  

    topics_list = check_topics.split(",")
    topics_and_levels = {}
    for topic in topics_list:
        topics_and_levels[topic.strip()] = 3
    await state.update_data(topics=topics_and_levels)

    await msg.answer(text.rate_topics, 
                     reply_markup=keyboards.rating_menu)
    await state.set_state(GetInfo.rate_topics)



@router.callback_query(F.data == "skip_rating", GetInfo.rate_topics)
@flags.chat_action("typing")
async def input_table_skip_rating(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.answer("You have skipped the rating, related info is set to default")
    await state.set_state(GetInfo.get_calendar)

    calendar_blank = await utils.calendar_template((await state.get_data())['deadline'])
    print(calendar_blank)
    await state.update_data(calendar=calendar_blank)
    await state.update_data(cur_date=0)
    await clbck.message.answer(text.calendar_text, reply_markup=keyboards.calendar_start_menu)

@router.message(GetInfo.rate_topics)
@flags.chat_action("typing")
async def input_table_rate_topics(msg: Message, state: FSMContext):
    topics_dict = (await state.get_data())['topics']
    topics = list(topics_dict.keys())
    grades = re.findall(r"\d", msg.text)

    for i in range(min(len(grades), len(topics))):
        topics_dict[topics[i]]=min(int(grades[i]), 5)
        topics_dict[topics[i]]=max(topics_dict[topics[i]], 1)

    await state.update_data(topics=topics_dict)
    await state.set_state(GetInfo.get_calendar)

    calendar_blank = await utils.calendar_template(
        (await state.get_data())['deadline']
        )
    await state.update_data(calendar=calendar_blank)
    await state.update_data(cur_date=0)   
    await msg.answer(text.calendar_text, reply_markup=keyboards.calendar_start_menu)


@router.callback_query(F.data == "skip_booking", GetInfo.get_calendar)
@flags.chat_action("typing")
async def input_table_skip_booking(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.answer("You have skipped the rating, related info is set to default")

    calendar = (await state.get_data())['calendar']
    for date in calendar:
        date.pop("12PM-1AM", None)
        date.pop("1AM-2AM", None)
        date.pop("2AM-3AM", None)
        date.pop("3AM-4AM", None)
        date.pop("4AM-5AM", None)
        date.pop("5AM-6AM", None)
        date.pop("11PM-12PM", None)
    await state.update_data(calendar=calendar)      

    await state.set_state(GetInfo.final)
    await clbck.message.answer(text.final_text, reply_markup=keyboards.finish_button)


@router.callback_query(booking_button_callback.filter(), GetInfo.get_calendar)
async def button_handler(clbck: CallbackQuery, callback_data: booking_button_callback, state: FSMContext):
    print(callback_data)
    action = callback_data.action
    date = callback_data.date
    hour = callback_data.hour

    if action==2:
        cur_date = int((await state.get_data())['cur_date'])
        await state.update_data(cur_date=cur_date+1) 
    elif action==1:   
        calendar = (await state.get_data())['calendar']
        dates = list(calendar.keys())
        calendar[dates[date]][hour] = not calendar[dates[date]][hour]
        await state.update_data(calendar=calendar)
    calendar = (await state.get_data())['calendar']
    dates = list(calendar.keys())
    cur_date = int((await state.get_data())['cur_date'])
    if cur_date==len(dates):
        await state.set_state(GenTable.gen_tasks)
        return await clbck.message.answer(text.final_text, reply_markup=keyboards.finish_button)
    await clbck.message.edit_text(text.calendar_booking.format(date=dates[cur_date]), 
                                  reply_markup=(await keyboards.calendar_kb(calendar[dates[cur_date]], cur_date)))

@router.callback_query(GenTable.gen_tasks, F.data == "final")
async def finish_form(clbck: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topics = data["topics"]
    calendar = data["calendar"]
    free_time = await utils.cal_for_prompt(calendar)
    await state.update_data(free_time=free_time)
    table_id = await db.create_table(clbck.from_user.id, topics, free_time)

    await clbck.message.edit_text("<em>📚 creating study plan...</em>")

    res = await utils.generate_text(prompt=text.gen_tasks_prompt.format(topics=json.dumps(topics)))
    if not res:
        time.sleep(60)
        res = await utils.generate_text(prompt=text.gen_tasks_prompt.format(topics=json.dumps(topics)))
    await db.update_balance(clbck.from_user.id, res[1])
    await state.update_data(tasks=res[0])
    print(res[0])

    await clbck.message.edit_text("<em>⏳ evaluating your time...</em>")
    tasks = res[0]
    res = await utils.generate_text(prompt=text.gen_timing_prompt.format(tasks=tasks))
    if not res:
        time.sleep(60)
        res = await utils.generate_text(prompt=text.gen_timing_prompt.format(tasks=tasks))
    await db.update_balance(clbck.from_user.id, res[1])
    await state.update_data(timing=res[0])
    print(res[0])

    await clbck.message.edit_text("<em>📆 adjusting to your schedule...</em>")
    timing = res[0]
    total_time = await utils.count_time(free_time)
    print(total_time)
    res = await utils.generate_text(prompt=text.gen_adj_prompt.format(
        timing=timing,
        total_time=total_time))
    if not res:
        time.sleep(60)
        res = await utils.generate_text(prompt=text.gen_adj_prompt.format(
        timing=timing,
        total_time=total_time))
    await db.update_balance(clbck.from_user.id, res[1])
    await state.update_data(timing_adj=res[0])
    print(res[0])
    
    await clbck.message.edit_text("<em>🙌 final steps...</em>")
    timing = res[0]
    res = await utils.generate_text(prompt=text.gen_table_prompt.format(
        calendar=json.dumps(free_time),
        timing=timing,
        tasks=tasks))
    if not res:
        time.sleep(60)
        res = await utils.generate_text(prompt=text.gen_table_prompt.format(
        calendar=json.dumps(free_time),
        timing=timing,
        tasks=tasks))
    await db.update_balance(clbck.from_user.id, res[1])
    await state.update_data(table=res[0])
    print(res[0])
    await db.add_table(table_id, res[0])
    await clbck.message.edit_text("<em>🙌 Done!</em>")
    await clbck.message.answer(res[0])

