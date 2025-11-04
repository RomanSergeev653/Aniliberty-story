import getpass
import os.path
import sys
import re
import unicodedata

import requests
from tqdm import tqdm

import Anime_models
from Anime_models import Anime, Franchise
from Timer import TimerManager


max_retries = 5

class Token:
    def __init__ (self, token: str = "", login: str = "", password: str = ""):
        self.token = token
        self.__login = login
        self.__password = password

        self.load_token()

    def __call__(self, *args, **kwargs):
        return self.token

    def __str__(self, *args, **kwargs):
        return self.token

    def authorization(self):
        for attempt in range(max_retries):

            if self.__login == "" or self.__password == "":
                sys.stdin.flush()
                self.__login = input("Логин: ")
                self.__password = input("Пароль: ")

            data = {
                "login": self.__login,
                "password": self.__password
            }
            url = "https://aniliberty.top/api/v1/accounts/users/auth/login"

            try:
                self.token = requests.post(data=data, url=url, timeout=10).json()['token']

                if self.token:
                    return

            except requests.exceptions.HTTPError as e:
                if 500 <= e.response.status_code < 600:
                    print(f"Серверная ошибка {e.response.status_code}. Повторная попытка - {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                elif e.response.status_code == 401 or e.response.status_code == 422:
                    print("Неверные данные авторизации, попробуйте ещё раз")
                    self.__login = ""
                    self.__password = ""
                    continue

                else:
                    print(f"Клиентская ошибка {e.response.status_code}")
                    raise

            except requests.exceptions.ConnectionError:
                print(f"Ошибка соединения...{attempt + 1}")
                continue

            return

    def load_token(self):
        if not os.path.exists("token"):
            self.authorization()
            with open("token", 'w', encoding='utf-8') as f:
                f.write(self.token)
        else:
            with open("token", "r", encoding='utf-8') as f:
                self.token = f.read()

    def refresh_token(self):
        self.token = ""

        if os.path.exists("token"):
           os.remove("token")

        self.load_token()





TOKEN = Token()


def get_collection(type_of_collection="WATCHED", limit = 10, exclude = "episodes") -> list[dict]:
    '''Получаем коллекцию пользователя. По умолчанию коллекию просмотренного'''
    global TOKEN
    anime_data = []
    total_pages = 0

    headers = {
        "Authorization": f"Bearer {TOKEN}",
    }
    params = {
        "type_of_collection": type_of_collection,
        "limit": limit,
        "exclude": exclude,
        "page": 1
    }
    url = "https://aniliberty.top/api/v1/accounts/users/me/collections/releases"
    total_pages = requests.get(url=url, params=params, headers=headers, timeout=10).json()['meta']['pagination']['total_pages']

    for page in tqdm(range(total_pages), desc="Get collection"):
        params["page"] = page + 1

        for attempt in range(max_retries):
            try:
                response = requests.get(url=url, params=params, headers=headers, timeout=10)

                response.raise_for_status()

                anime_data.extend(response.json()["data"])
                break

            except requests.exceptions.HTTPError as e:
                if 500 <= e.response.status_code < 600:
                    print(f"Серверная ошибка {e.response.status_code}. Повторная попытка - {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                else:
                    print(f"Клиентская ошибка {e.response.status_code}")
                    raise

            except requests.exceptions.ConnectionError:
                print(f"Ошибка соединения...{attempt + 1}")
                continue

            raise Exception(f"Не удалось выполнить запрос после {max_retries} попыток")
    return anime_data


def get_franchises(id: int) -> list[Franchise]:
    '''Получаем все связзанные тайтлы для этого релиза'''
    franchise_releases = []
    headers = {
        "Authorization": f"Bearer {TOKEN}",
    }
    params = {
        "include": "franchise_releases",
    }
    url = f"https://aniliberty.top/api/v1/anime/franchises/release/{id}"

    for attempt in range(max_retries):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=10)

            response.raise_for_status()

            franchise_releases.extend(response.json())
            break

        except requests.exceptions.HTTPError as e:
            if 500 <= e.response.status_code < 600:
                print(f"Серверная ошибка {e.response.status_code}. Повторная попытка - {attempt + 1}")
                if attempt < max_retries - 1:
                    continue
            else:
                print(f"Клиентская ошибка {e.response.status_code}")
                raise

        except requests.exceptions.ConnectionError:
            print(f"Ошибка соединения...{attempt + 1}")
            continue

    franchises = []

    if franchise_releases != []:
        for release in franchise_releases[0]['franchise_releases']:
            franchises.append(Franchise(
                id=release['release_id'],
                name=release['release']['name']['main']
                )
            )

    return franchises


def sanitize_filename(filename: str) -> str:
    """
    Очищает строку для использования в качестве имени файла (да-да эту часть написала ИИшка)
    """
    # Нормализуем юникод (преобразуем символы с диакритиками и т.д.)
    filename = unicodedata.normalize('NFKD', filename)

    # Удаляем недопустимые символы для файлов
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Заменяем пробелы и другие пробельные символы на подчеркивания
    # filename = re.sub(r'\s+', '_', filename)

    # Удаляем точки в начале и конце (могут быть скрытыми файлами)
    filename = filename.strip('.')

    # Ограничиваем длину (например, 100 символов)
    if len(filename) > 100:
        filename = filename[:100]

    return filename


def create_anime_md(anime: Anime) -> str:
    '''Создаём MD файл для аниме'''
    status_emoji = "🟢" if anime.is_ongoing else "🔴"
    status_text = "Онгоинг" if anime.is_ongoing else "Завершено"
    genres_str = ""
    franchises_str = ""

    for genre in anime.genres:
        genres_str += "#" + re.sub(r'\s+', '_', genre.name) + " "

    for franchise in anime.franchises:
        franchises_str += "[[" + sanitize_filename(franchise.name) + "]]\n"


    md_content = f"""

**{anime.name.english}**

---

## 📖 Описание
{anime.description}

## ℹ️ Основная информация

| Параметр | Значение |
|----------|----------|
| **Тип** | {anime.type.description} |
| **Год** | {anime.year} |
| **Сезон** | {anime.season.description} |
| **Эпизоды** | {anime.episodes_total} |
| **Статус** | {status_emoji} {status_text} |
| **Рейтинг** | {anime.age_rating.label} |

## 🏷️ Жанры
{genres_str}

## Связанные
{franchises_str}

## 📊 Статистика

- ❤️ **В избранном:** `{anime.added_in_users_favorites}`
- 📋 **В планах:** `{anime.added_in_planned_collection}`
- ✅ **Просмотрено:** `{anime.added_in_watched_collection}`
- 👀 **Смотрят:** `{anime.added_in_watching_collection}`
- ⏸️ **Отложено:** `{anime.added_in_postponed_collection}`
- 🗑️ **Брошено:** `{anime.added_in_abandoned_collection}`

## 🔗 Ссылки
- **Alias:** `{anime.alias}`
- **ID:** `{anime.id}`
- **Постер:** ![Poster]({anime.poster.optimized.src})
    """
    return md_content


def save_anime_to_md(anime: Anime, output_dir: str = "anime_notes") -> str:
    """
    Сохраняет аниме в MD файл

    Returns:
        Путь к сохраненному файлу
    """
    # Создаем директорию если нет
    os.makedirs(output_dir, exist_ok=True)

    # Создаем безопасное имя файла
    filename = sanitize_filename(anime.name.main)
    filepath = os.path.join(output_dir, filename+".md")

    # Создаем содержимое
    md_content = create_anime_md(anime)

    # Сохраняем файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return filepath


# anime_data = []
# headers = {
#         "Authorization": f"Bearer {TOKEN}",
#     }
# params = {
#     "type_of_collection": "WATCHED",
#     "limit": 1,
#     "exclude": "episodes",
#     "page": 300
# }
# url = "https://aniliberty.top/api/v1/accounts/users/me/collections/releases"
# try:
#     response = requests.get(url=url, params=params, headers=headers, timeout=10)
#
#     response.raise_for_status()
#
#     anime_data.extend(response.json()["data"])
# except Exception as e:
#     print(f"Ошибка {e}")
#
# anime = Anime.from_json(anime_data[0])
# anime.franchises = get_franchises(anime.id)
# print(save_anime_to_md(anime=anime))

anime_data = get_collection()
anime_dataset = []
timer = TimerManager()
timer.start("Build md storage")
for i in tqdm(anime_data,desc="Building md storage"):
    timer.start("parsing json")
    new_one_anime = Anime.from_json(i)
    timer.stop("parsing json")

    timer.start("geting franchises")
    new_one_anime.franchises = get_franchises(new_one_anime.id)
    timer.stop("geting franchises")

    timer.start("saving to md")
    save_anime_to_md(new_one_anime)
    timer.stop("saving to md")

    anime_dataset.append(new_one_anime)
timer.stop("Build md storage")
print(timer.get_report())

# filename = "Моя геройская академия: Два героя"
# print(f"{sanitize_filename(filename=filename)}.md")

# wached_collection = get_collection(limit=10)
#
# print(Anime.from_json(wached_collection[0]))

