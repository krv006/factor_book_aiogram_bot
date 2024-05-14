from uuid import uuid4

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from run.config import ADMIN_LIST, database
from state.state import Form
from filtres import IsAdmin
from state.rv import upload_file

admin_router = Router()


@admin_router.message(CommandStart(), IsAdmin(ADMIN_LIST))
async def is_admin(message: Message):
    btns = [[KeyboardButton(text="Add category")],
            [KeyboardButton(text="Add product")],
            [KeyboardButton(text="Remove category")],
            [KeyboardButton(text="Remove product")]]
    rkb = ReplyKeyboardBuilder(btns)
    rkb.adjust(2)
    await message.answer('Welcome! Choose.', reply_markup=rkb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == 'Remove product')
async def remove_product(message: Message):
    products = database.get('products')
    ikb = InlineKeyboardBuilder()
    if products == {}:
        await message.answer('No products yet')
    else:
        for product in products.keys():
            ikb.add(InlineKeyboardButton(text=products[product]['product_name'], callback_data=f'rpro_{product}'))
        ikb.adjust(2, repeat=True)
        await message.answer('Which product da you want to remove?', reply_markup=ikb.as_markup(resize_keyboard=True))


@admin_router.callback_query(F.data.startswith('rpro'))
async def rpro_callback(callback: CallbackQuery):
    products = database.get('products')
    categories = database.get('categories')
    product_id = callback.data.split('_')[-1]
    del products[product_id]
    for category in categories.keys():
        for product in categories[category]:
            if product == product_id:
                categories[category].remove(product)
    ikb = InlineKeyboardBuilder()
    for product in products:
        ikb.add(InlineKeyboardButton(text=products[product]['product_name'], callback_data=f'rpro_{product}'))
    ikb.adjust(2, repeat=True)
    await callback.message.edit_text('Product removed.\nWhich product da you want to remove?',
                                     reply_markup=ikb.as_markup(resize_keyboard=True))
    database['products'] = products
    database['categories'] = categories


@admin_router.callback_query(F.data.startswith('remove_product_'))
async def remove_product(callback: CallbackQuery):
    product = callback.data.split('_')[-1]
    products = database.get('products')
    del products[product]
    database['products'] = products
    ikb = InlineKeyboardBuilder()
    for product in products:
        ikb.add(InlineKeyboardButton(text=product['product_name'], callback_data=f'remove_product_{product}'))
    ikb.adjust(2, repeat=True)
    await callback.message.edit_text('Product removed.\nWhich product da you want to remove?',
                                     reply_markup=ikb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == 'Remove category')
async def remove_category(message: Message):
    if database.get('categories') == {}:
        await message.answer('No categories yet')
    else:
        categories = database.get('categories')
        ikb = InlineKeyboardBuilder()
        for category in categories:
            ikb.add(InlineKeyboardButton(text=category, callback_data=f'remove_{category}'))
        ikb.adjust(2, repeat=True)
        await message.answer('Which category da you want to remove?', reply_markup=ikb.as_markup(resize_keyboard=True))


@admin_router.callback_query(F.data.startswith('remove_'))
async def remove_callback_query(callback: CallbackQuery):
    category = callback.data.split('_')[-1]
    categories = database.get('categories')
    del categories[category]
    database['categories'] = categories
    ikb = InlineKeyboardBuilder()
    for category in categories:
        ikb.add(InlineKeyboardButton(text=category, callback_data=f'remove_{category}'))
    ikb.adjust(2, repeat=True)
    await callback.message.edit_text('Category removed.\nWhich category da you want to remove?',
                                     reply_markup=ikb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == "Add category")
async def add_category(message: Message, state: FSMContext):
    await state.set_state(Form.category)
    await message.answer('Enter category name: ')


@admin_router.message(Form.category)
async def okey(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()
    await state.clear()
    categories = database.get('categories')
    category = data['category']
    categories[category] = []
    database['categories'] = categories
    ikb = InlineKeyboardBuilder()
    for i in categories.items():
        ikb.add(InlineKeyboardButton(text=i[0], callback_data=f'product_{i[0]}'))
    ikb.adjust(2, repeat=True)
    await message.answer("Category added", reply_markup=ikb.as_markup())


@admin_router.message(F.text == "Add product")
async def add_product(message: Message, state: FSMContext):
    btns = [[KeyboardButton(text="Add category")],
            [KeyboardButton(text="Add product")],
            [KeyboardButton(text="Remove category")],
            [KeyboardButton(text="Remove product")]]
    rkb = ReplyKeyboardBuilder(btns)
    rkb.adjust(2)
    if database.get('categories') == {}:
        await message.answer('Before add product please add category of product',
                             reply_markup=rkb.as_markup(resize_keyboard=True))
    else:
        await state.set_state(Form.product_name)
        await message.answer('Enter product name: ')


@admin_router.message(Form.product_name)
async def add_product(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text)
    await state.set_state(Form.product_price)
    await message.answer('Enter price of product: ')


@admin_router.message(Form.product_price)
async def add_product(message: Message, state: FSMContext):
    await state.update_data(product_price=message.text)
    await state.set_state(Form.product_image)
    await message.answer('Enter image of product: ')


@admin_router.message(Form.product_image)
async def png_to_url(message: Message, state: FSMContext):
    file = await message.bot.get_file(message.photo[-1].file_id)
    img_byte = (await message.bot.download(file.file_id)).read()
    url = await upload_file(img_byte)
    await state.update_data(product_image=url)
    await state.set_state(Form.product_description)
    await message.answer('Enter description of product: ')


@admin_router.message(Form.product_description)
async def choose_category(message: Message, state: FSMContext):
    await state.update_data(product_description=message.text)
    categories = database['categories']
    ikb = InlineKeyboardBuilder()
    for i in categories.items():
        ikb.add(InlineKeyboardButton(text=i[0], callback_data=f'ushla_{i[0]}_cat'))
    ikb.adjust(2, repeat=True)
    await message.answer("Choose category", reply_markup=ikb.as_markup())


@admin_router.callback_query(F.data.endswith('cat'))
async def category_callback(call: CallbackQuery, state: FSMContext):
    category = call.data.split('_')[1]
    categories = database['categories']
    products = database.get('products')
    data = await state.get_data()
    product_id = str(uuid4())
    await state.clear()
    product = {"product_name": data.get('product_name'),
               'product_price': data.get('product_price'),
               'product_image': data.get('product_image'),
               'product_description': data.get('product_description')}
    products[product_id] = product
    categories[category].append(product_id)
    database['categories'] = categories
    database['products'] = products
    await call.message.answer("Added to category")
    print(products)
    print(categories)
