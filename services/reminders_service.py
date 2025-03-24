import json
import re
from datetime import datetime

from bson import ObjectId

from loader import reminder_col

async def save_reminder_to_db(reminder_data):
    """
    Сохраняет напоминание в MongoDB.

    :param user_id: ID пользователя Telegram.
    :param text: Текст напоминания.
    :param reminder_datetime: Дата и время напоминания.
    """
    await reminder_col.insert_one(reminder_data)


async def get_reminders_by_user_id(user_id: int):
    """
    Получает все напоминания для указанного user_id.

    :param user_id: ID пользователя Telegram.
    :return: Список напоминаний в формате словарей.
    """
    # Находим все напоминания для данного user_id
    reminders = await reminder_col.find({"user_id": str(user_id)}).to_list()

    return reminders


def format_reminders(input_string):
    try:
        # Заменяем ObjectId(...) на строку внутри кавычек
        input_string = re.sub(r"ObjectId\('([^']+)'\)", r'"\1"', input_string)

        # Заменяем одинарные кавычки на двойные для корректного JSON
        input_string = input_string.replace("'", '"')

        # Преобразуем строку JSON в объект Python
        reminders = json.loads(input_string)

        # Формируем человекочитаемый список
        result = []
        for reminder in reminders:
            text = reminder.get("reminder_text", "Без текста")
            raw_datetime = reminder.get("reminder_datetime", None)

            # Форматируем дату и время
            if raw_datetime:
                try:
                    dt = datetime.fromisoformat(raw_datetime)
                    formatted_datetime = dt.strftime("%d %B %Y, %H:%M")  # Пример: "25 March 2025, 18:25"
                    # Локализация месяца на русский язык
                    month_translation = {
                        "January": "января", "February": "февраля", "March": "марта",
                        "April": "апреля", "May": "мая", "June": "июня",
                        "July": "июля", "August": "августа", "September": "сентября",
                        "October": "октября", "November": "ноября", "December": "декабря"
                    }
                    for eng, rus in month_translation.items():
                        formatted_datetime = formatted_datetime.replace(eng, rus)
                except ValueError:
                    formatted_datetime = "Некорректная дата"
            else:
                formatted_datetime = "Время не указано"

            result.append(f"Напоминание: {text} (время: {formatted_datetime})")

        # Возвращаем результат как строку с переносами строк
        return "\n".join(result)

    except Exception as e:
        return f"Ошибка обработки данных: {str(e)}"

async def get_reminders_by_object_ids(obj_id_list_str):
    # 1. Извлечение ObjectId из строки
    object_ids = re.findall(r"ObjectId\('([^']+)'\)", obj_id_list_str)
    if not object_ids:
        return "Ошибка: Входная строка не содержит ObjectId"

    # 2. Преобразование строк в ObjectId
    object_ids = [ObjectId(oid) for oid in object_ids]

    # 3. Поиск объектов по ObjectId
    query = {"_id": {"$in": object_ids}}
    results = await reminder_col.find(query).to_list(None)  # Получаем все найденные документы

    # 4. Возвращаем результат как массив объектов
    return results


async def process_reminder_operation(operation_str):
    try:
        # Словарь для человекочитаемых названий полей
        FIELD_NAMES = {
            'reminder_text': 'Текст напоминания',
            'reminder_datetime': 'Дата и время'
        }

        # 1. Предварительная очистка строки от ObjectId()
        operation_str = re.sub(
            r'ObjectId\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'"\1"',
            operation_str,
            flags=re.IGNORECASE
        ).strip()

        # 2. Удаляем лишние запятые в массивах
        operation_str = re.sub(r',(\s*[\]\}])', r'\1', operation_str)

        # 3. Парсинг JSON
        operation = json.loads(operation_str, strict=False)

        # 4. Рекурсивное преобразование ObjectId
        def convert_objectids(obj):
            if isinstance(obj, list):
                return [convert_objectids(item) for item in obj]
            if isinstance(obj, dict):
                return {k: convert_objectids(v) for k, v in obj.items()}
            if isinstance(obj, str) and re.match(r'^[a-f0-9]{24}$', obj, re.IGNORECASE):
                return ObjectId(obj)
            return obj

        operation = convert_objectids(operation)

        # 5. Проверка обязательных полей
        if 'operation' not in operation:
            return "🔥 Отсутствует поле 'operation'"
        if 'filter' not in operation:
            return "🔥 Отсутствует поле 'filter'"

        op_type = operation['operation']
        filter_query = operation['filter']

        # Вспомогательная функция для форматирования даты
        def format_date(date_value):
            if not date_value:
                return 'Не указана'
            if isinstance(date_value, datetime):
                return date_value.strftime("%d.%m.%Y %H:%M")
            try:
                dt = datetime.fromisoformat(date_value)
                return dt.strftime("%d.%m.%Y %H:%M")
            except (ValueError, TypeError):
                return str(date_value)

        if op_type == 'update':
            # Проверка наличия update-данных
            if 'update' not in operation:
                return "🔥 Отсутствует поле 'update'"
            if '$set' not in operation['update']:
                return "🔥 Для операции update требуется оператор $set"
            if not operation['update']['$set']:
                return "🔥 Нет полей для обновления в $set"

            # Получаем документы до обновления
            old_docs = await reminder_col.find(filter_query).to_list(None)

            # Выполняем обновление
            update_data = operation['update']
            result = await reminder_col.update_many(
                filter_query,
                update_data
            )

            if result.modified_count > 0:
                changes = []
                for doc in old_docs:
                    change_log = []
                    for field, new_value in update_data['$set'].items():
                        field_name = FIELD_NAMES.get(field, field)
                        old_value = doc.get(field)
                        # Форматируем даты
                        if field == 'reminder_datetime':
                            old_value = format_date(old_value)
                            new_value = format_date(new_value)
                        change_log.append(
                            f"  {field_name}: \"{old_value}\" → \"{new_value}\""
                        )
                    changes.append("Изменения:\n" + "\n".join(change_log))
                return f"✅ Успешно обновлено {result.modified_count} напоминаний:\n" + "\n\n".join(changes)
            return "Нечего обновлять"

        elif op_type == 'delete':
            # Получаем документы перед удалением
            docs = await reminder_col.find(filter_query).to_list(None)

            # Выполняем удаление
            result = await reminder_col.delete_many(filter_query)

            if result.deleted_count > 0:
                deleted = []
                for doc in docs:
                    text = doc.get('reminder_text', 'Без текста')
                    date = format_date(doc.get('reminder_datetime'))
                    deleted.append(
                        f"  Текст: \"{text}\"\n  Дата: {date}"
                    )
                return f"🗑️ Удалено {result.deleted_count} напоминаний:\n\n" + "\n\n".join(deleted)
            return "Нечего удалять"

        else:
            return f"❌ Неизвестная операция: {op_type}"

    except json.JSONDecodeError as e:
        return (f"🔥 Ошибка парсинга JSON на позиции {e.pos}: {e.msg}\n"
                f"Фрагмент ошибки: {operation_str[e.pos - 20:e.pos + 20]}...")
    except Exception as e:
        return f"🔥 Критическая ошибка: {str(e)}"