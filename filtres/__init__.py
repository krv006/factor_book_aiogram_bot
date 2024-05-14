from typing import Iterable

from aiogram.filters import Filter
from aiogram.types import Message


class IsAdmin(Filter):
    def __init__(self, admin_list: Iterable[int]):
        self.admin_list = admin_list

    async def __call__(self, msg: Message):
        return msg.from_user.id in self.admin_list
