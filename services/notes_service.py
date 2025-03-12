import logging

from loader import github_token
from pathlib import Path
from git import Repo
from urllib.parse import quote

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
            file.write("\n" + text_to_append)

        repo.git.add(all=True)

        # Делаем коммит
        repo.index.commit(commit_message)
        repo.remotes.origin.push()

    except Exception as e:
        logging.error(e)
        print(f"Произошла ошибка: {e}")
