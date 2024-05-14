from collections import defaultdict

from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from run.config import database

inline_mode_router = Router()


@inline_mode_router.inline_query()
async def inline_mode(inline_query: InlineQuery):
    l = []
    products = database.get('products')
    if inline_query.query == '':
        if inline_query.model_dump()['chat_type'] == 'sender':
            for i, product in enumerate(products.items()):
                product_name = product[1]['product_name']
                product_description = product[1]['product_description']

                iqr = InlineQueryResultArticle(id=product[0],
                                               title=product[1]['product_name'],
                                               input_message_content=InputTextMessageContent(
                                                   message_text=f'{product_name}\n\n{product_description}\nBuyurtma qilish uchun @calculation123bot\nbook_id: {product[0]}'),
                                               description=f'Factor Books\n💸 price: {product[1]["product_price"]}',
                                               thumb_url=product[1]['product_image'],
                                               )
                l.append(iqr)
                if i >= 50:
                    break
        else:
            products = database.get('products')
            for i, product in enumerate(products.items()):
                iqr = InlineQueryResultArticle(id=product[0],
                                               title=product[1]['product_name'],
                                               input_message_content=InputTextMessageContent(message_text=f'''
                                               {product[1]['product_name']}\n\n{product[1]['product_description']}\nBuyurtma qilish uchun @calculation123bot\nbook_id: {product[0]}

                                               '''),
                                               description=f'Factor Books\n💸 price: {product[1]["product_price"]}',
                                               thumb_url=product[1]['product_image'],
                                               )
                l.append(iqr)
                if i >= 50:
                    break
    else:
        products = {product[0]: product[1] for product in products.items() if
                    inline_query.query.lower() in product[1]['product_name'].lower()}
        if inline_query.model_dump()['chat_type'] == 'sender':
            for i, product in enumerate(products.items()):
                product_name = product[1]['product_name']
                product_description = product[1]['product_description']
                iqr = InlineQueryResultArticle(id=product[0],
                                               title=product[1]['product_name'],
                                               input_message_content=InputTextMessageContent(
                                                   message_text=f'{product_name}\n\n{product_description}\nBuyurtma qilish uchun @calculation123bot\nbook_id: {product[0]}'),
                                               description=f'Factor Books\n💸 price: {product[1]["product_price"]}',
                                               thumb_url=product[1]['product_image'],
                                               )
                l.append(iqr)
                if i >= 50:
                    break
        else:
            products = database.get('products')
            for i, product in enumerate(products.items()):
                product_name = product[1]['product_name']
                product_description = product[1]['product_description']
                iqr = InlineQueryResultArticle(id=product[0],
                                               title=product[1]['product_name'],
                                               input_message_content=InputTextMessageContent(
                                                   message_text=f'{product_name}\n\n{product_description}\nBuyurtma qilish uchun @calculation123bot\nbook_id: {product[0]}'),
                                               description=f'Factor Books\n💸 price: {product[1]["product_price"]}',
                                               thumb_url=product[1]['product_image'],
                                               )
                l.append(iqr)
                if i >= 50:
                    break
    await inline_query.answer(l)


@inline_mode_router.message(lambda msg: msg.text[-36:] in database.get('products').keys())
async def calculation(message: Message):
    product_id = message.text[-36:]
    products = database.get('products')
    product = products[product_id]
    product_name = product['product_name']
    product_price = product['product_price']
    product_description = product['product_description']
    product_image = product['product_image']
    users = database.get('users')
    user_id = str(message.from_user.id)
    users[user_id] = defaultdict(dict)
    users[user_id][product_id] = {'product_name': product_name, 'product_price': product_price, 'product_quantity': 1}
    text = f'Name: {product_name}\nPrice: {product_price}\nDescription: {product_description}'
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='-', callback_data=f'product_id_{product_id}_decrease'),
            InlineKeyboardButton(text=str(users[user_id][product_id]['product_quantity']),
                                 callback_data='aaa'),
            InlineKeyboardButton(text='+', callback_data=f'product_id_{product_id}_increase'),
            InlineKeyboardButton(text=_('⏪ Back'), callback_data='back_to_category'),
            InlineKeyboardButton(text=_('🛒 Add to basket '), callback_data=f'add_basket_{product_id}'))
    ikb.adjust(3, repeat=True)
    database['users'] = users
    await message.delete()
    await message.answer_photo(photo=product_image, caption=text,
                               reply_markup=ikb.as_markup(resize_keyboard=True))
