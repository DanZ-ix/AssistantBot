from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from motor.motor_asyncio import AsyncIOMotorClient

import logging
import boto3
from yandex_cloud_ml_sdk import AsyncYCloudML

from configs import (bot_token, yandex_api_token, yandex_api_key_id, github_token,
                     yandex_api_static_key_id, yandex_api_static_key,
                     yandex_gpt_folder_id)
from utils.json_schemas import yandex_gpt_response_schema

admin_list = ["154134326"]

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=yandex_api_static_key_id,
    aws_secret_access_key=yandex_api_static_key
)

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger('aiohttp').setLevel(logging.INFO)

sdk = AsyncYCloudML(folder_id=yandex_gpt_folder_id, auth=yandex_api_token)
yandex_gpt = sdk.models.completions('yandexgpt', model_version="rc")
yandex_gpt = yandex_gpt.configure(temperature=0, max_tokens=800)


MONGO_URI = "mongodb://localhost:27017"  # Замените на ваш URI
DB_NAME = "assistant_bot"  # Имя базы данных

# Создание клиента MongoDB
client = AsyncIOMotorClient(MONGO_URI)

# Выбор базы данных
db = client[DB_NAME]

# Пример коллекции (таблицы) для хранения данных пользователей
buy_list = db["buy_list"]
reminder_col = db["reminders"]

bot = Bot(token=bot_token)
dp = Dispatcher(storage=MemoryStorage())
