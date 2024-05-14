from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()


@help_router.message(Command("help"))
async def help(message: Message):
    await message.answer('Commands:\n/start -> to start bot\n/help -> help\n')
