from loader import yandex_gpt, logging

system_get_meta_prompt = '''
Ты — помощник для анализа запросов пользователя на естественном языке. Твоя задача — определить, что хочет пользователь, и вернуть результат в формате массива JSON.
Пользователь в одном сообщении может сделать несколько запросов, в таком случае нужно вернуть несколько элементов массива
Возможные действия:
1. **Сохранить заметку**:
   - Пользователь хочет сохранить текст в заметки.
   - Верни JSON в формате, удаляя из текста команду сохранения заметки, оставить только суть:
     {
       "action": "save_note",
       "parameters": {
         "note_text": "текст заметки"
       }
     }

2. **Общий запрос к LLM**:
   - Пользователь делает запрос в общем виде, предоставь ответ на его запрос.
   - Верни JSON в формате:
     {
       "action": "general_question",
       "parameters": {
         "response": "Ответ на запрос пользователя"
       }
     }
'''


async def get_task_meta(text):
    query = [
        {
            "role": "system",
            "text": system_get_meta_prompt
        },
        {
            "role": "user",
            "text": text
        }
    ]

    gpt_result = await send_query(query)
    print(gpt_result)

    return gpt_result.strip("```")

async def send_query(query):
    result = await yandex_gpt.run(query)
    return result[0].text


