import getpass
import os.path
import sys

import requests
from tqdm import tqdm



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




wached_collection = get_collection(limit=10)

print(wached_collection[0].keys())
