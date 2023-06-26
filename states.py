from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    text_prompt = State()


class GetInfo(StatesGroup):
    get_deadline = State()
    get_topics = State()
    rate_topics = State()