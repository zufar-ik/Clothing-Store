from aiogram.dispatcher.filters.state import StatesGroup, State


class Reklama(StatesGroup):
    reklama = State()

class Category(StatesGroup):
    main = State()
    first = State()
    second = State()
    third = State()
    fourth = State()
    fifth = State()
    sixth = State()
    mamm = State()

class Zakaz(StatesGroup):
    start = State()
    name = State()
    Adress = State()
    tel = State()
    tel2 = State()
    confirmP =State()