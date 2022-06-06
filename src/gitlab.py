import urllib3
import requests
import yaml
from hashlib import sha256
import sys
from pathlib import Path
from multiprocessing.pool import ThreadPool

urllib3.disable_warnings()

URL = "https://git.llcmms.loc"


def auth():
    path = str(Path().absolute()) + '/src/api_key/api-key.yaml'
    try:
        with open(path, 'r') as data:
            return yaml.safe_load(data)['gitlab']['api_key']
    except Exception as exc:
        print(f"Can't read file {str(exc)}")
        # print(f"Error: {traceback.print_exc()}")
        sys.exit(3)


def request_url(url):
    # HTTP headers
    headers = {
        "Private-Token": auth(),
        "Content-Type": "application/json"
    }

    try:
        req = requests.get(url, headers=headers, verify=False)
        print([req.headers, req.json()])

    except Exception as exc:
        print("Except in get_new:", exc)
        return
    if req.status_code != 200:
        raise Exception(f"Request error, status code: {req.status_code}. URL: {url}")
    return [req.headers, req.json()]


# def multi_processor(urls):
#     pool = ThreadPool(len(urls))
#     print("Pool size:", len(urls))
#     procs = []
#     for url in urls:
#         procs.append(pool.apply_async(multi_get, args=(url,)))
#     try:
#         pool.close()
#         pool.join()
#         result = [x.get() for x in procs]
#         print(len(result))
#         print(len(result[0]))
#         #print("Result", result[0])
#         return result
#     except Exception as exc:
#         print("{Processor} Exception:", str(exc))

# def multi_get(url):
#     """
#     Функция, реализующая GET метод
#     :param url: урл
#     :return: список
#     """
#     # HTTP заголовки
#     headers = {
#         "Private-Token": auth(),
#         "Content-Type": "application/json"
#     }
#     try:
#         req = requests.get(url, headers=headers)
#     except Exception as exc:
#         print("Except in multi_get:", exc)
#         return
#     if req.status_code != 200:
#         print(url, "\n", f"Return code {req.status_code}")
#         return None
#     # Общее кол-во элементов объекта
#     # !!!! Нужна проверка
#     if req.headers.get("X-Total"):
#         total = int(req.headers.get("X-Total"))
#         # Общее кол-во страниц с элементами объекта
#         # !!!! Нужна проверка
#         total_pgs = int(req.headers.get("X-Total-Pages"))
#         print(f"Total Pages: {total_pgs}\nTotal Items: {total}")
#
#         batch = req.json()
#         # Собираем в единый список все элементы объекта
#         urls = []
#         for page in range(1, total_pgs+1):
#             print(f"Page: {page}")
#             #req = requests.get(url + "?page={}".format(page), headers=headers)
#             urls.append(url + "?page={}".format(page))
#             #print(len(req.json()))
#             batch.extend(req.json())
#             #print(len(batch))
#         #print(batch)
#         batch = multi_get(urls)
#         return batch
#     else:
#         return req.json()


def collect_items(url):
    """
    Функция, реализующая GET метод
    :param url: урл
    :return: список
    """

    headers, json_data = request_url(url)
    # Total elements count
    # ToDo: need except
    if headers.get("X-Total") and int(headers.get("X-Total-Pages")) > 1:
        total_items = int(headers.get("X-Total"))
        # Total pages count
        # ToDo: need except
        total_pages = int(headers.get("X-Total-Pages"))
        pages_range = [x for x in range(1, total_pages + 1)]
        print(
            f"Pages Counts: {len(pages_range)}\n"
            f"Items Counts: {total_items}"
        )

        batch = []
        # Collect all objects in one batch
        for page in pages_range:
            # print(f"Page: {page}")
            _, json_data = request_url(url + "?page={}".format(page))
            # print(len(req.json()))
            batch.extend(json_data)
            # print(len(batch))
        # print(batch)
        return batch


def projects(limit=""):
    """
    Функция возвращает словарь
    { id проекта: {название проекта, адрес проекта}}
    содержащий все проекты.
    :param limit:
    :return:
    """

    project_list = []
    projects_data = collect_items(f"{URL}/api/v4/projects")
    for project in projects_data:
        project_list.append({
            "id": project.get("id"),
            "project": {
                "artifacts_dir": sha_convert(project.get("id")),
                "name": project.get("name"),
                "path": project.get("path_with_namespace"),
                "last_activity_at": project.get("last_activity_at"),
                "created_at": project.get("created_at"),
                "web_url": project.get("web_url"),
                "namespace": project.get("namespace"),
                "empty_repo": project.get("empty_repo"),
                "creator": project.get("creator_id"),
            }
        })
    return project_list


def search(scope, name):
    """
    :param scope: projects
    :param element: find pattern zfx-capital-service
    :return:
    """
    url = f"https://git.llcmms.loc/api/v4/search?scope={scope}&search={name}"
    _, data = request_url(url)
    if not data:
        raise Exception(f' {scope} {name} not found')
    return data


def get_project_variables(project_id):
    project_variables_data = collect_items(f"{URL}/api/v4/projects/{project_id}/variables")
    # print(json.dumps(project_variables_data, indent=4))
    return project_variables_data


def sha_convert(string):
    hash = sha256(str(string).encode("utf-8")).hexdigest()
    return "/".join([hash[0:2], hash[2:4], hash])