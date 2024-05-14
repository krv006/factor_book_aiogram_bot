from os import getenv

from dotenv import load_dotenv
from redis_dict import RedisDict

database = RedisDict('factor_book')
# database.clear()
# print(database)
load_dotenv('../.env')
TOKEN = getenv("TOKEN1")
ADMIN_LIST = 1305675046,
