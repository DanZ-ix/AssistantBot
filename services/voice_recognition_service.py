import requests
import asyncio
import uuid
import json

from loader import s3, yandex_api_token

bucket_name = "voice-bucket-tg-assistant"
recognize_url = "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"
get_rec_status_url = "https://operation.api.cloud.yandex.net/operations/"


async def recognize_audio(audio_file) -> str:
    s3_key = f"voice_messages/{uuid.uuid4()}.ogg"
    s3.upload_fileobj(
        audio_file,
        bucket_name,
        s3_key
    )

    headers = {
        "Authorization": f"Api-Key {yandex_api_token}",
        "Content-Type": "application/json"
    }
    request_body = form_request_body(s3_key)
    response = requests.post(
        recognize_url,
        headers=headers,
        data=json.dumps(request_body)  # Преобразуем JSON в строку
    )

    if response.status_code == 200:
        result = response.json()
        operation_id = result.get("id")
        text = await get_recognition(operation_id, s3_key)
        return text
    else:
        return "Ошибка"


async def get_recognition(operation_id, s3_key):
    headers = {
        "Authorization": f"Api-Key {yandex_api_token}"
    }

    for i in range(20):
        await asyncio.sleep(2)
        rec_status = requests.get(get_rec_status_url + operation_id, headers=headers)

        if rec_status.status_code == 200:
            if rec_status.json().get("done", False):
                req = rec_status.json()
                res_text = ""
                for chunk in req['response']['chunks']:
                    res_text += chunk['alternatives'][0]['text'] + " "

                s3.delete_object(Bucket=bucket_name, Key=s3_key)
                return res_text
    raise Exception


def form_request_body(file_key):
    request_body = {
        "config": {
            "specification": {
                "languageCode": "ru-RU"
            }
        },
        "audio": {
            "uri": "https://storage.yandexcloud.net/voice-bucket-tg-assistant/" + file_key
        }
    }
    return request_body

