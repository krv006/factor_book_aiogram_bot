from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

contact_router = Router()


@contact_router.message(F.text == __("🔵 Our social media"))
async def send_message(message: Message):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text='IKAR | Factor Books', url='https://t.me/ikar_factor'))
    ikb.row(InlineKeyboardButton(text='Factor Books', url='https://t.me/factor_books'))
    ikb.row(InlineKeyboardButton(text='\"Factor Books\" nashiryoti', url='https://t.me/factorbooks'))
    await message.answer(_('🔵 Our social media'), reply_markup=ikb.as_markup())


@contact_router.message(F.text == __("📞 Contact us"))
async def message(message: Message) -> None:
    text = _(
        "\n\nTelegram: @kamron_rustamov_dev\n📞  +{number}\n🤖 This bot made by Rustamov Kamron (@rv\n".format(
            number=998901078055))
    await message.answer(text=text)
