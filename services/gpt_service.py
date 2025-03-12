from loader import yandex_gpt, logging



get_meta_prompt = '''
Ты — помощник для анализа запросов пользователя на естественном языке. Твоя задача — определить, что хочет пользователь, и вернуть результат в формате JSON.

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
    query = get_meta_prompt + "\n\nТекст пользователя: " + text
    gpt_result = await send_query(query)
    return gpt_result.strip("```")


async def send_query(query):
    result = await yandex_gpt.run(query)
    return result[0].text


