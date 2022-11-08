from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

yes_no = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да, все верно!'),KeyboardButton(text='Нет, не верно!')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


contactnum = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Поделиться номером", request_contact=True)
        ]
    ],
    resize_keyboard=True,
)

send_loc = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Поделиться геопозицией', request_location=True)]
    ],
    resize_keyboard=True,
)