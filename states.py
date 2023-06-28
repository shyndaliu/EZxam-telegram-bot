from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    text_prompt = State()


class GetInfo(StatesGroup):
    get_deadline = State()
    get_topics = State()
    rate_topics = State()
    get_calendar = State()
    final = State()

class GenTable(StatesGroup):
    gen_tasks = State()
    gen_timing = State()
    gen_adj = State()
    gen_table = State()