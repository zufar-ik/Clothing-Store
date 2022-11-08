import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import db


async def make_category_keyboards():
    category = await db.view_category()
    keyboards = InlineKeyboardMarkup(row_width=2)
    for i in category:
        keyboards.insert(InlineKeyboardButton(text=i['name'], callback_data=f"category:{i['slug']}:{i['id']}"))
    keyboards.insert(InlineKeyboardButton(text='Назад',callback_data='back4'))
    return keyboards

def make_count():
    keyboards = InlineKeyboardMarkup(row_width=3)
    for i in range(1,10):
        keyboards.insert(InlineKeyboardButton(text=f'{i}',callback_data=f'{i}'))
    keyboards.insert(InlineKeyboardButton(text='Назад',callback_data='back1'))
    return keyboards

def make_size():
    keyboards = InlineKeyboardMarkup(row_width=3)
    size = ['S','M','L','XL','XXL','Oversize']
    for i in size:
        keyboards.insert(InlineKeyboardButton(text=f'{i}',callback_data=f'{i}'))
    keyboards.insert(InlineKeyboardButton(text='Назад',callback_data='back2'))
    return keyboards

def make_main():
    keyboards = InlineKeyboardMarkup(row_width=1)
    keyboards.insert(InlineKeyboardButton(text='Каталог',callback_data='catalog'))
    keyboards.insert(InlineKeyboardButton(text='Instagram',url='www.instagram.com/zufar_ik'))
    keyboards.insert(InlineKeyboardButton(text='Корзина',callback_data='korzinka'))
    return keyboards

user = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить",callback_data="send_to_admin")],
        [InlineKeyboardButton(text="Отмена",callback_data="cancel")]
    ]
)
