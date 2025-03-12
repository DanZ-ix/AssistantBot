from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import logging
import boto3
from yandex_cloud_ml_sdk import AsyncYCloudML

from configs import (bot_token, yandex_api_token, yandex_api_key_id, github_token,
                     yandex_api_static_key_id, yandex_api_static_key,
                     yandex_gpt_folder_id)


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
yandex_gpt = sdk.models.completions('yandexgpt-lite')
yandex_gpt = yandex_gpt.configure(temperature=0.8, max_tokens=500)


bot = Bot(token=bot_token)
dp = Dispatcher(storage=MemoryStorage())
