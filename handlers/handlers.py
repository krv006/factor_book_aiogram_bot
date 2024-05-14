from collections import defaultdict
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, URLInputFile
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from run.config import database, ADMIN_LIST
from state.state import Form

user_router = Router()


def make_menu(**kwargs):
    rkb = ReplyKeyboardBuilder()
    rkb.row(KeyboardButton(text=_("📚 Books", **kwargs)))
    rkb.row(KeyboardButton(text=_("📃 My orders", **kwargs)))
    rkb.row(KeyboardButton(text=_("🔵 Our social media", **kwargs)),
            KeyboardButton(text=_("📞 Contact us", **kwargs)))
    rkb.row(KeyboardButton(text=_('Change language', **kwargs)))
    return rkb.as_markup(resize_keyboard=True)


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(_('Welcome! Choose.'), reply_markup=make_menu())


@user_router.message(F.text == __('Change language'))
async def change_language(message: Message) -> None:
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text=_('🇺🇿uzbek'), callback_data='lang_uz'),
            InlineKeyboardButton(text=_('🇬🇧english'), callback_data='lang_en'),
            InlineKeyboardButton(text=_('🇰🇷korean'), callback_data='lang_ko'))
    await message.answer(_('Change language'), reply_markup=ikb.as_markup())


@user_router.callback_query(F.data.startswith('lang_'))
async def languages(callback: CallbackQuery, state: FSMContext) -> None:
    lang_code = callback.data.split('lang_')[-1]
    await state.update_data(locale=lang_code)
    if lang_code == 'uz':
        lang = _('Uzbek', locale=lang_code)
    elif lang_code == 'en':
        lang = _('english', locale=lang_code)
    else:
        lang = _('Kores', locale=lang_code)
    await callback.answer(_('{lang} is selected', locale=lang_code).format(lang=lang))

    rkb = make_menu(locale=lang_code)
    msg = _('Welcome! Choose.', locale=lang_code)
    await callback.message.answer(text=msg, reply_markup=rkb)


@user_router.message(F.text == __('📚 Books'))
async def text_handler(message: Message) -> None:
    categories = database.get('categories')
    basket = database.get('basket')
    user_id = str(message.from_user.id)
    if not basket.get(user_id):
        basket[user_id] = {}
    ikb = InlineKeyboardBuilder()
    for i in categories.keys():
        ikb.add(InlineKeyboardButton(text=i, callback_data=f'category_{i}'))
    ikb.add(InlineKeyboardButton(text=_('🔍Search'), switch_inline_query_current_chat=''))
    if basket[user_id] != {}:
        ikb.add(InlineKeyboardButton(text=_('🛒 Basket({len_basket})'.format(len_basket=len(basket[user_id].keys()))),
                                     callback_data='basket'))
    ikb.adjust(2, repeat=True)
    await message.answer(_('Choose category'), reply_markup=ikb.as_markup(resize_keyboard=True))


@user_router.callback_query(F.data.startswith('category_'))
async def callback_handler(callback: CallbackQuery) -> None:
    category = callback.data.split('_')[-1]
    categories = database.get('categories')
    products = database.get('products')
    user_id = str(callback.from_user.id)
    basket = database.get('basket')
    ikb = InlineKeyboardBuilder()
    if not basket.get(user_id):
        basket[user_id] = {}
    for i in categories[category]:
        product_name = products[i]['product_name']
        ikb.add(InlineKeyboardButton(text=product_name, callback_data=f'p1_{i}'))
    if basket[user_id] != {}:
        ikb.add(InlineKeyboardButton(text=_('🛒 Basket({len_basket})'.format(len_basket=len(basket[user_id].keys()))),
                                     callback_data='basket'))
    ikb.add(InlineKeyboardButton(text=_('⏪ Back'), callback_data='back_to_category'))

    ikb.adjust(2, repeat=True)
    await callback.message.edit_text(f'{category}', reply_markup=ikb.as_markup())


@user_router.callback_query(F.data.startswith('p1_'))
async def product_name_handler(callback: CallbackQuery) -> None:
    product_id = callback.data.split('_')[-1]
    products = database.get('products')
    product_name = products[product_id]['product_name']
    product_price = products[product_id]['product_price']
    product_description = products[product_id]['product_description']
    product_image = products[product_id]['product_image']
    users = database.get('users')
    user_id = str(callback.from_user.id)
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
    await callback.message.delete()
    await callback.message.answer_photo(photo=product_image, caption=text,
                                        reply_markup=ikb.as_markup(resize_keyboard=True))


@user_router.callback_query(F.data == 'back_to_category')
async def back_to_category_handler(callback: CallbackQuery) -> None:
    categories = database.get('categories')
    basket = database.get('basket')
    user_id = str(callback.from_user.id)
    ikb = InlineKeyboardBuilder()
    if not basket.get(user_id):
        basket[user_id] = {}
    for i in categories.keys():
        ikb.add(InlineKeyboardButton(text=i, callback_data=f'category_{i}'))

    ikb.add(InlineKeyboardButton(text=_('🔍Search'), switch_inline_query_current_chat=' '))
    if basket[user_id] != {}:
        ikb.add(InlineKeyboardButton(text=_('🛒 Basket({len_basket})'.format(len_basket=len(basket[user_id].keys()))),
                                     callback_data='basket'))
    ikb.adjust(2, repeat=True)
    await callback.message.delete()
    await callback.message.answer('Choose category', reply_markup=ikb.as_markup(resize_keyboard=True))


@user_router.callback_query(F.data == 'basket')
async def basket(callback: CallbackQuery) -> None:
    basket = database.get('basket')
    ikb = InlineKeyboardBuilder()
    user_id = str(callback.from_user.id)
    all = 0
    text = '🛒 Basket\n\n'
    for i, product_id in enumerate(basket[user_id]):
        product_name = basket[user_id][product_id]['product_name']
        product_quantity = int(basket[user_id][product_id]['product_quantity'])
        product_price = int(basket[user_id][product_id]['product_price'])
        text += f'{i + 1}.{product_name}\n{product_quantity} x {product_price} = {product_price * product_quantity}\n\n'
        all += product_quantity * product_price
    text += f'Total: {all} som'
    ikb.add(InlineKeyboardButton(text=_('❌ Clear the basket'), callback_data='cancel'),
            InlineKeyboardButton(text=_('✅ Confirm the order'), callback_data='confirm'),
            InlineKeyboardButton(text=_('⏪ Back'), callback_data='back_to_category'))
    ikb.adjust(1, repeat=True)
    await callback.message.edit_text(text=text, reply_markup=ikb.as_markup())


@user_router.callback_query(F.data == "confirm")
async def confirm_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text='Phone number📞', request_contact=True))
    await callback.message.answer(_('Send phone number'), reply_markup=rkb.as_markup(resize_keyboard=True))
    await state.set_state(Form.user_phone_number)


@user_router.message(F.content_type == ContentType.CONTACT, Form.user_phone_number)
async def contact_callback(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    basket = database.get('basket')
    ikb = InlineKeyboardBuilder()
    user_id = str(message.from_user.id)
    all = 0
    text = '🛒 Basket\n\n'
    for i, product_id in enumerate(basket[user_id]):
        product_name = basket[user_id][product_id]['product_name']
        product_quantity = int(basket[user_id][product_id]['product_quantity'])
        product_price = int(basket[user_id][product_id]['product_price'])
        text += f'{i + 1}.{product_name}\n{product_quantity} x {product_price} = {product_price * product_quantity}\n\n'
        all += product_quantity * product_price
    text += f'Total: {all} som\nYour phone number {phone_number}\n\nDo you order?'
    ikb.add(InlineKeyboardButton(text='❌ No', callback_data='no'),
            InlineKeyboardButton(text='✅ Yes', callback_data='yes'),
            )
    ikb.adjust(2, repeat=True)
    await message.answer(text=text, reply_markup=ikb.as_markup())
    await state.clear()


@user_router.callback_query(F.data == 'no')
async def no_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.delete()
    await callback.message.answer(text=_('❌ Cancelled'))
    await callback.message.answer(_('Main manu'), reply_markup=make_menu())


@user_router.callback_query(F.data == 'yes')
async def yes_callback(callback: CallbackQuery, bot: Bot):
    user_id = str(callback.from_user.id)
    basket = database.get('basket')
    order_count = database.get('order_count')
    order_count += 1
    product_id_list: list = []
    for product_id in basket[user_id].keys():
        product_id_list.append(product_id)
    order_user = database.get('order_user')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not order_user.get(user_id):
        order_user[user_id] = defaultdict(dict)
    order_user[user_id][str(order_count)] = {'products': [], 'order_mode': '🔄 in standby mode', 'order_time': time}

    order_mode = order_user[user_id][str(order_count)]['order_mode']
    order_text = f'Order number: {order_count}\nDate of order: {time}\nOrder status: {order_mode}\n'
    all_sum = 0
    for index, product_id in enumerate(product_id_list):
        product_name = basket[user_id][product_id]['product_name']
        product_price = int(basket[user_id][product_id]['product_price'])
        product_quantity = int(basket[user_id][product_id]['product_quantity'])
        order_user[user_id][str(order_count)]['products'].append(
            {'product_name': product_name, 'product_price': product_price, 'product_quantity': product_quantity})
        order_text += f'{index + 1}.Book name: {product_name}\n{product_quantity} x {product_price} = {product_quantity * product_price}'
        all_sum += product_quantity * product_price
    order_text += f'\n\nTotal: {all_sum} som'
    del basket[user_id]
    database['basket'] = basket
    database['order_user'] = dict(order_user)

    for admin in ADMIN_LIST:
        ikb = InlineKeyboardBuilder()
        ikb.row(InlineKeyboardButton(text='✅ Confirm', callback_data=f'admin_confirm_{order_count}_{user_id}'),
                InlineKeyboardButton(text='❌ Cancel', callback_data='admin_cancel'))
        await bot.send_message(chat_id=admin, text=f'From {callback.from_user.full_name} has an order\n{order_text}',
                               reply_markup=ikb.as_markup())
    await callback.message.delete()
    await callback.message.answer(
        _('Dear customer! Thank you for your order.Order number: {order_count}'.format(order_count=order_count)),
        reply_markup=make_menu())
    database['order_count'] = order_count


@user_router.callback_query(F.data.startswith('admin_confirm'))
async def admin_confirm(callback: CallbackQuery, bot: Bot):
    user_id = callback.data.split('_')[-1]
    order_count = callback.data.split('_')[2]
    await bot.send_message(chat_id=user_id,
                           text=_('<em>🎉 Your order number {order_count} has been accepted by the admin.</em>'.format(
                               order_count=order_count)),
                           reply_markup=make_menu())
    order_user = database['order_user']
    order_user[user_id][str(order_count)]['order_mode'] = '✅ accepted'
    database['order_user'] = order_user

    await callback.message.delete()


@user_router.message(F.text == __('📃 My orders'))
async def my_orders(message: Message):
    user_id = str(message.from_user.id)
    order_user = database.get('order_user')
    if order_user.get(user_id):
        for i in order_user[user_id]:
            order_mode = order_user[user_id][i]['order_mode']
            order_time = order_user[user_id][i]['order_time']
            text = f'Order number: {i}\nDate of order: {order_time}\nOrder status: {order_mode}\n\n'
            all = 0
            for index, order in enumerate(order_user[user_id][i]['products']):
                product_name = order['product_name']
                product_price = int(order['product_price'])
                product_quantity = int(order['product_quantity'])
                text += f'{index + 1}.Book name: {product_name}\n{product_quantity} x {product_price} = {product_quantity * product_price}\n'
                all += product_quantity * product_price
            text += f'\n\nTotal: {all} som'
            await message.answer(text)
    else:
        await message.answer(_("You don't have any orders or ADMIN don't accept your order"))


@user_router.callback_query(F.data == 'admin_cancel')
async def admin_cancel(callback: CallbackQuery):
    await callback.message.delete()


@user_router.callback_query(F.data == 'cancel')
async def cancel(call: CallbackQuery):
    user_id = str(call.from_user.id)
    users = database.get('users')
    basket = database.get('basket')
    categories = database.get('categories')
    del users[user_id]
    del basket[user_id]
    database['users'] = users
    database['basket'] = basket
    await call.message.delete()
    await call.answer(_('Basket is cleared'), show_alert=True)
    user_id = str(call.from_user.id)
    if not basket.get(user_id):
        basket[user_id] = {}
    ikb = InlineKeyboardBuilder()
    for i in categories.keys():
        ikb.add(InlineKeyboardButton(text=i, callback_data=f'category_{i}'))
    ikb.add(InlineKeyboardButton(text='🔍Search', switch_inline_query_current_chat=' '))
    if basket[user_id] != {}:
        ikb.add(InlineKeyboardButton(text=_('🛒 Basket({len_basket})'.format(len_basket=len(basket[user_id].keys()))),
                                     callback_data='basket'))
    ikb.adjust(2, repeat=True)
    await call.message.answer(_('Choose category'), reply_markup=ikb.as_markup())


@user_router.callback_query(F.data.endswith('crease'))
async def increase_category_handler(callback: CallbackQuery) -> None:
    users = database.get('users')
    product_id = callback.data.split('_')[2]
    products = database.get('products')
    product_image = products[product_id].get('product_image')
    product_name = products[product_id].get('product_name')
    product_price = products[product_id].get('product_price')
    product_description = products[product_id]['product_description']
    amal = callback.data.split('_')[-1]
    user_id = str(callback.from_user.id)

    if amal == 'increase':
        users[user_id][product_id]['product_quantity'] += 1
    elif amal == 'decrease':
        if users[user_id][product_id]['product_quantity'] == 1:
            await callback.answer(_('You can order at least 1 book'), show_alert=True)
            return
        else:
            users[user_id][product_id]['product_quantity'] -= 1
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='-', callback_data=f'product_id_{product_id}_decrease'),
            InlineKeyboardButton(text=str(users[user_id][product_id]['product_quantity']),
                                 callback_data='aaa'),
            InlineKeyboardButton(text='+', callback_data=f'product_id_{product_id}_increase'),
            InlineKeyboardButton(text=_('⏪ Back'), callback_data='back_to_category'),
            InlineKeyboardButton(text=_('🛒 Add to basket '), callback_data=f'add_basket_{product_id}'))
    ikb.adjust(3, repeat=True)
    text = f'Name: {product_name}\nPrice: {product_price}\nDescription: {product_description}'
    database['users'] = users
    image = URLInputFile(product_image)
    media = InputMediaPhoto(media=image, caption=text)
    await callback.message.edit_media(media=media, reply_markup=ikb.as_markup())


@user_router.callback_query(F.data.startswith('add_basket'))
async def add_basket(callback: CallbackQuery):
    products = database.get('products')
    product_id = callback.data.split('_')[-1]
    users = database.get('users')
    user_id = str(callback.from_user.id)
    product_name = products[product_id].get('product_name')
    product_price = products[product_id].get('product_price')
    product_quantity = users[user_id][product_id].get('product_quantity')
    basket = database.get('basket')
    basket[user_id] = database.get('basket').get(user_id, {})
    if not basket[user_id].get(product_id):
        basket[user_id][product_id] = {'product_name': product_name, 'product_price': product_price,
                                       'product_quantity': product_quantity}
    else:
        basket[user_id][product_id]['product_quantity'] += product_quantity
    database['basket'] = basket
    await callback.message.delete()
    await callback.answer(_('Product added to basket'), show_alert=True)
    categories = database.get('categories')
    ikb = InlineKeyboardBuilder()
    if not basket.get(user_id):
        basket[user_id] = {}
    for i in categories.keys():
        ikb.add(InlineKeyboardButton(text=i, callback_data=f'category_{i}'))
    ikb.add(InlineKeyboardButton(text=_('🔍Search'), switch_inline_query_current_chat=' '))
    if basket[user_id] != {}:
        ikb.add(InlineKeyboardButton(text=_('🛒 Basket({len_basket})'.format(len_basket=len(basket[user_id].keys()))),
                                     callback_data='basket'))
    ikb.adjust(2, repeat=True)
    await callback.message.answer(_('Choose category'), reply_markup=ikb.as_markup())
