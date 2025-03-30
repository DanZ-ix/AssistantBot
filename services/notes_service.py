import logging
import re

from bson import ObjectId

from loader import github_token, notes_col
from pathlib import Path
from git import Repo
from urllib.parse import quote


async def save_note_mongo(note_text, user_id):
    note = {
        "text": note_text,
        "user_id": user_id
    }
    notes_col.insert_one(note)


async def get_notes_objects(user_id):
    return await notes_col.find({"user_id": user_id}).to_list(length=None)


def get_object_ids_list(objectids_str: str) -> list:
    # Регулярное выражение для извлечения ObjectId из строки
    objectid_pattern = re.compile(r"ObjectId\('([a-fA-F0-9]{24})'\)")
    # Извлекаем все совпадения
    object_ids = [
        ObjectId(match.group(1))
        for match in objectid_pattern.finditer(objectids_str)
    ]
    return object_ids


async def get_notes_by_objectids(objectids: list) -> list:
    # Если нет ObjectId - возвращаем пустой список
    if not objectids:
        return []
    # Запрос к MongoDB
    cursor = notes_col.find({"_id": {"$in": objectids}})
    return await cursor.to_list(length=None)


async def del_notes_by_obj_ids(objectids: list):
    # Если нет ObjectId - возвращаем пустой список
    if not objectids:
        return "Не удалено"
    # Запрос к MongoDB
    await notes_col.delete_many({"_id": {"$in": objectids}})
    return f"Удалено записей: {len(objectids)}"

def get_notes_str(notes_list: list) -> str:
    if not notes_list:
        return "Нет сохраненных заметок"

    # Формируем нумерованный список
    formatted = "Ваши заметки:\n" + "\n".join(
        f"{i + 1}. {text['text']}"
        for i, text in enumerate(notes_list)
    )
    return formatted


def add_note(note_text):
    append_to_inbox_and_push(note_text, "added new note", github_token)


def append_to_inbox_and_push(text_to_append: str, commit_message: str, github_token: str):
    """
    Добавляет текст в конец файла inbox.md в локальном репозитории,
    выполняет pull, коммит и push изменений в GitHub.

    :param text_to_append: Текст, который нужно добавить в конец файла.
    :param commit_message: Сообщение для коммита.
    :param github_token: Токен доступа GitHub для авторизации.
    """
    # Путь к папке data (рядом со скриптом)
    script_dir = Path(__file__).parent
    repo_path = script_dir.parent / "data" / "obsidianNotes"

    # Путь к файлу inbox.md
    inbox_file_path = repo_path / "Inbox.md"

    # Проверяем, существует ли файл inbox.md
    if not inbox_file_path.exists():
        raise FileNotFoundError(f"Файл {inbox_file_path} не найден.")

    try:
        # Открываем репозиторий
        repo = Repo(repo_path)

        # Настройка удалённого репозитория с использованием токена
        remote_url = f"https://{quote(github_token, safe='')}:x-oauth-basic@github.com/DanZ-ix/obsidianNotes"
        if remote_url.startswith("https://"):
            # Заменяем URL на версию с токеном
            repo.remotes.origin.set_url(remote_url)

        # Выполняем pull
        repo.remotes.origin.pull()

        # Добавляем текст в конец файла inbox.md
        with open(inbox_file_path, 'a', encoding='utf-8') as file:
            file.write("\n\n\n" + text_to_append)

        repo.git.add(all=True)

        # Делаем коммит
        repo.index.commit(commit_message)
        repo.remotes.origin.push()

    except Exception as e:
        logging.error(e)
        print(f"Произошла ошибка: {e}")
