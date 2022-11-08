from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from data.config import ADMINS
from keyboards.default.start_keyboard import yes_no, contactnum
from keyboards.inline.menu_keyboards import make_category_keyboards, make_count, make_size, make_main, user
from loader import db
from loader import dp
from states.state import Category, Zakaz
import re


@dp.callback_query_handler(state=Category.main)
async def main(call: types.CallbackQuery):
    msg = 'Ваши заказы!\n\n'
    markup = (InlineKeyboardMarkup(row_width=2))
    if call.data == 'catalog':
        await call.message.delete()
        await call.message.answer('Выберите категорию', reply_markup=await make_category_keyboards())
        await Category.first.set()
    else:
        product = await db.check_product(tg_id=str(call.from_user.id))
        if not product:
            await call.message.edit_text('Ваша корзинка еще пуста, быть может мы это исправим!?',
                                         reply_markup=await make_category_keyboards())
            await Category.first.set()

        else:
            for i in product:
                msg += (
                    f'Название товара: {i["name"]}\n'
                    f'Размер: {i["size"]}\n'
                    f'Цена: {i["price"]} сум\n'
                    f'Кол-во: {i["count"]}\n\n'
                    f'{i["price"]} x {i["count"]} = {int(i["price"]) * int(i["count"])} сум\n\n'
                    f'|_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_|\n\n')
                markup.insert(InlineKeyboardButton(text=f'❌{i["name"]} {i["size"]}❌',
                                                   callback_data=f'{i["id"]}:{i["name"]}:{i["size"]}'))
            markup.insert(InlineKeyboardButton(text='Меню', callback_data='menu'))
            markup.insert(InlineKeyboardButton(text='Оформить заказ!', callback_data='order'))
            await call.message.answer(msg, reply_markup=markup)
            await Category.mamm.set()


@dp.callback_query_handler(state=Category.mamm)
async def main(call: types.CallbackQuery):
    callback = call.data.split(':')
    print(callback[0])
    if call.data == 'menu':
        await call.message.delete()
        await call.message.answer('Выберите раздел!', reply_markup=make_main())
        await Category.main.set()
    elif call.data == 'order':
        total = 0
        product = await db.check_product(tg_id=str(call.from_user.id))
        msg = ''
        for i in product:
            narx = int(i['price']) * int(i['count'])
            total += narx
            msg += (f'{i["name"]} - {i["price"]} x {i["count"]} = {int(i["price"]) * int(i["count"])} сум\n\n'
                    f'|_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_|\n\n')
        msg += f'Всего: {total} сум'
        # await call.answer('Раздел добавиться скоро!', show_alert=True)
        await call.message.delete()
        await call.message.answer(msg)
        await call.message.answer('Все верно?', reply_markup=yes_no)
        await Zakaz.start.set()

    else:
        await db.delete_product(tg_id=str(call.from_user.id), id=int(callback[0]))
        await call.message.edit_text(f'{callback[1]} {callback[2]} удален из вашей корзинки!', reply_markup=make_main())
        await Category.main.set()


@dp.callback_query_handler(state=Category.first)
async def product_in_category(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back4':
        await call.message.delete()
        await call.message.answer('Выберите раздел!', reply_markup=make_main())
        await Category.main.set()
    else:
        category_id = call.data.split(':')
        print(category_id)
        await state.update_data(
            {'CALLBACK': category_id}
        )
        category = await db.where_category(slug=category_id[1])
        product = await db.where_product_for_category(category_id=int(category_id[2]))
        markup = InlineKeyboardMarkup(row_width=2)
        for i in product:
            markup.insert(InlineKeyboardButton(text=f'{i["name"]}', callback_data=f'product:{i["slug"]}:{i["id"]}'))
        markup.insert(InlineKeyboardButton(text='Назад', callback_data='back3'))
        markup.insert(InlineKeyboardButton(text='Главное меню', callback_data='mainmenu'))
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{category[0]["img"]}', 'rb'),
                                        caption=f'{category[0]["title"]}', reply_markup=markup)
        await Category.second.set()


@dp.callback_query_handler(state=Category.second)
async def product_one(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back3':
        await call.message.delete()
        await call.message.answer('Выберите категорию', reply_markup=await make_category_keyboards())
        await Category.first.set()
    elif call.data == 'mainmenu':
        await call.message.delete()
        await call.message.answer('Выберите раздел!', reply_markup=make_main())
        await Category.main.set()

    else:
        callback = call.data.split(':')
        await state.update_data(
            {'product': callback}
        )
        product = await db.where_product(slug=callback[1])
        markup = InlineKeyboardMarkup(row_width=1)
        markup.insert(InlineKeyboardButton(text='В корзинку!', callback_data='add_cart'))
        markup.insert(InlineKeyboardButton(text='Назад', callback_data='back'))
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{product[0]["img"]}', 'rb'),
                                        caption=f'<b>{product[0]["name"]}</b>\n\n'
                                                f'{product[0]["about"]}\n\n'
                                                f'Цена: <b>{product[0]["price"]} сум</b>\n\n'
                                                f'Цена Oversize: <b>{product[0]["price_over"]}</b>\n\n'
                                                f'Размеры: От S-XXL, Oversize', reply_markup=markup)
        await Category.third.set()


@dp.callback_query_handler(state=Category.third)
async def back_or_cart(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data.get('CALLBACK')
    category = await db.where_category(slug=category_id[1])
    if call.data == 'back':
        product = await db.where_product_for_category(category_id=int(category_id[2]))
        markup = InlineKeyboardMarkup(row_width=2)
        for i in product:
            markup.insert(InlineKeyboardButton(text=f'{i["name"]}', callback_data=f'product:{i["slug"]}:{i["id"]}'))
        markup.insert(InlineKeyboardButton(text='Назад', callback_data='back3'))
        markup.insert(InlineKeyboardButton(text='Главное меню', callback_data='mainmenu'))
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{category[0]["img"]}', 'rb'),
                                        caption=f'{category[0]["title"]}', reply_markup=markup)
        await Category.second.set()

    else:
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{category[0]["img"]}', 'rb'), caption='Выберите размер',
                                        reply_markup=make_size())
        await Category.fourth.set()


@dp.callback_query_handler(state=Category.fourth)
async def get_size(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back2':
        data = await state.get_data()
        callback = data.get('product')
        product = await db.where_product(slug=callback[1])
        markup = InlineKeyboardMarkup(row_width=1)
        markup.insert(InlineKeyboardButton(text='В корзинку!', callback_data='add_cart'))
        markup.insert(InlineKeyboardButton(text='Назад', callback_data='back'))
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{product[0]["img"]}', 'rb'),
                                        caption=f'<b>{product[0]["name"]}</b>\n\n'
                                                f'{product[0]["about"]}\n\n'
                                                f'Цена: <b>{product[0]["price"]} сум</b>\n\n'
                                                f'Цена Oversize: <b>{product[0]["price_over"]}</b>\n\n'
                                                f'Размеры: От S-XXL, Oversize', reply_markup=markup)
        await Category.third.set()
    else:
        await state.update_data(
            {'size': call.data}
        )
        data = await state.get_data()
        category_id = data.get('CALLBACK')
        category = await db.where_category(slug=category_id[1])
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{category[0]["img"]}', 'rb'), caption='Выберите кол-во',
                                        reply_markup=make_count())

        await Category.fifth.set()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@dp.callback_query_handler(state=Category.fifth)
async def add_cart_or_back1(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back1':
        data = await state.get_data()
        category_id = data.get('CALLBACK')
        category = await db.where_category(slug=category_id[1])
        await call.message.delete()
        await call.message.answer_photo(photo=open(f'backend/{category[0]["img"]}', 'rb'), caption='Выберите размер',
                                        reply_markup=make_size())
        await Category.fourth.set()
    else:
        data = await state.get_data()
        product_data = data.get('product')
        size = data.get('size')
        count = int(call.data)
        id = str(call.from_user.id)
        product = await db.where_product(slug=product_data[1])
        if is_number(count):
            for i in product:
                check = await db.check_product(tg_id=str(id), name=i['name'], size=size)
                if check:
                    if size == 'Oversize':
                        await db.update_product(count=(int(check[0]['count']) + int(count)), tg_id=str(id),
                                                name=str(check[0]['name']), size=str(size),
                                                )
                    else:
                        await db.update_product(count=(int(check[0]['count']) + int(count)), tg_id=str(id),
                                                name=str(check[0]['name']), size=str(size),
                                                )
                    await call.answer('Заказ добавлен в корзинку')
                    await call.message.delete()
                    await call.message.answer('Выберите пункт!', reply_markup=await make_category_keyboards())
                    await Category.first.set()
                else:
                    if size == 'Oversize':
                        await db.add_cart(tg_id=str(id), name=i['name'], count=int(count), price=int(i['price_over']),
                                          size=size)
                    else:
                        await db.add_cart(tg_id=str(id), name=i['name'], count=int(count), price=int(i['price']),
                                          size=size)
                    await call.answer('Заказ добавлен в корзинку')
                    await call.message.delete()
                    await call.message.answer('Выберите пункт!', reply_markup=await make_category_keyboards())
                    await Category.first.set()


@dp.message_handler(text="Да, все верно!", state=Zakaz.start)
async def ye(message: types.Message):
    await message.answer("Заполните нужные пункты пожалуйста")
    await message.answer("Как вас зовут?")
    await Zakaz.name.set()


@dp.message_handler(text="Нет, не верно!", state=Zakaz.start)
async def no(message: types.Message):
    await message.delete()
    await message.answer('Вы отменили заказ!', reply_markup=ReplyKeyboardRemove())
    await message.answer('Выберите раздел!', reply_markup=make_main())


@dp.message_handler(state=Zakaz.name)
async def name(message: types.Message, state: FSMContext):
    id1 = message.from_user.id
    await state.update_data(
        {"id": id1}
    )
    name = message.text
    await state.update_data(
        {"name": name}
    )
    await message.answer("Введите адрес доставки\n\n"
                         "Область, Город, Улицу и номер дома")
    await Zakaz.next()


@dp.message_handler(state=Zakaz.Adress)
async def adress(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(
        {'adress': text}
    )
    await message.answer("Введите основной номер!", reply_markup=contactnum)
    await Zakaz.next()


@dp.message_handler(content_types=['contact'], state=Zakaz.tel)
async def get_img(message: types.Message, state: FSMContext):
    phone = message.contact['phone_number']
    num = "^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"
    if re.match(num, phone):
        await state.update_data(
            {'phone': phone}
        )
        await message.answer("Введите второстепенный номер!\n"
                             "(если его нет отправьте любой знак)", reply_markup=ReplyKeyboardRemove())
        await Zakaz.next()
    else:
        await message.answer("Вы ввели некорректный номер\n"
                             "Введите еще раз!")
        await Zakaz.tel


@dp.message_handler(state=Zakaz.tel2)
async def get_img(message: types.Message, state: FSMContext):
    tel2 = message.text
    await state.update_data(
        {'tel2': tel2}
    )
    data1 = await state.get_data()
    name = data1.get("name")
    adress1 = data1.get("adress")
    telnum1 = data1.get("phone")
    telnum2 = data1.get("tel2")
    Username = message.from_user.username
    await state.update_data(
        {"username": Username}
    )
    username = data1.get("username")
    idq = message.from_user.id
    lat = (adress1)
    await message.answer(
        text=f"Имя и фамилия: {name}\n"
             f"Основной номер: +{telnum1}\n"
             f"Адрес: {lat}\n"
             f"Username: @{Username}\n"
             f"Второстепенный: +{telnum2}", reply_markup=user
    )
    await Zakaz.next()


@dp.callback_query_handler(text="cancel", state=Zakaz.confirmP)
async def back(call: types.CallbackQuery):
    await call.message.answer("Вы отменили заказ!", reply_markup=make_main())
    await call.message.delete()


@dp.callback_query_handler(text="send_to_admin", state=Zakaz.confirmP)
async def sendadmin(call: types.CallbackQuery, state: FSMContext):
    call.cache_time = 60
    data1 = await state.get_data()
    name = data1.get("name")
    adress1 = data1.get("adress")
    telnum1 = data1.get("phone")
    telnum2 = data1.get("tel2")
    id1 = data1.get("id")
    Username = call.message.from_user.username
    await state.update_data(
        {"username": Username}
    )
    username = data1.get("username")
    products = await db.check_product(tg_id=str(id1))
    total = 0
    img = []
    msg = "Новый заказ!!\n\n"
    for product in products:
        namm = product['name']
        print(namm)
        photo = await db.where_product(name=namm)
        for i in photo:
            print(i)
            img.append(i['img'])
        narx = (int(product['price']) * int(product['count']))
        total += narx
        msg += f"{product['name']}\n\n{product['price']} x {product['count']} = {narx} сум\n\nРазмер: {product['size'].upper()} \n\n-------------------------------------\n"
    msg += f"\nОбщая сумма: {total} сум"
    idq = ADMINS[0]
    lat = (adress1)
    await call.bot.send_document(chat_id=ADMINS[0], document=(open(f"backend/{img[0]}", "rb")),
                                 caption=f"{msg}\n"
                                         f"Имя и фамилия: {name}\n"
                                         f"Основной номер: +{telnum1}\n"
                                         f"Адрес: {lat}\n"
                                         f"Username: @{username}\n"
                                         f"Второстепенный: +{telnum2}"
                                 )
    await call.message.answer("Ваш заказ принят!\n"
                              "Вам в личку или по телефону свяжутся администраторы  ", reply_markup=make_main())
    await call.message.delete()
    await db.delete_cart(tg_id=str(id1))
    await Category.main.set()
