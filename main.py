import requests

TOKEN = "eyJpdiI6IjZDYURxRU14MDc5UjBvbEhUR1BQQ1E9PSIsInZhbHVlIjoiMkVTVlpOTFlUSFlSSTErS2ZTbXdHckZHRnV2c2xadHhoV0t2WXgvcmlVM3lrZmRDbGUwOWhxb3ErUWJNa21yZSIsIm1hYyI6ImFlZTcwMzk5YWUyMzAzMTM4NTI1ZjM1MzY5ZDRlNzQ4ZTkwNDQyOTdkNjQ3Y2Q2MGY1ZGQwZTM1OTlkNDk4MTUiLCJ0YWciOiIifQ=="


def authorization(login, password):
    data = {
        "login": login,
        "password": password
    }
    url = "https://aniliberty.top/api/v1/accounts/users/auth/login"

    try:
        response = requests.post(data=data, url=url, timeout=10)
    except requests.exceptions.Timeout:
        print("Таймаут ответа при авторизации")
        return {}

    return response.json()


def get_collection(type_of_collection="WATCHED", limit = 10, exclude = "episodes"):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
    }
    params = {
        "type_of_collection": type_of_collection,
        "limit": limit,
        "exclude": "data"
    }
    url = "https://aniliberty.top/api/v1/accounts/users/me/collections/releases"

    print(requests.get(url=url, params=params, headers=headers, timeout=100))

    for i in range(5):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=100)
        except requests.exceptions.HTTPError as errh:
            if i == 4:
                raise "BREAK"
            else:
                print("HTTP Error")
                print(errh.args[0])
        except requests.exceptions.ConnectionError:
            print(f"Ошибка соединения...{i}")
            continue
        break

    print(response)

    print(response.json())


if TOKEN == "":
    print(authorization(login="romansergeev653@yandex.ru", password="Pass_me17"))
else:
    print("Токен уже есть, погнали!")

get_collection()
