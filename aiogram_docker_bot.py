import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from redis_dict import RedisDict

load_dotenv('.env')

database = RedisDict('users_redis', host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
TOKEN = os.getenv("DOCKER")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("salom aka ")


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
