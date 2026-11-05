"""Module for extracting dependencies from Alpine Linux APKINDEX."""

import io
import tarfile
import urllib.error
import urllib.request
from typing import List


def fetch_apkindex(repo_url: str) -> str:
    """Downloads APKINDEX.tar.gz and returns the text content of APKINDEX."""
    # Формируем ссылку на индекс
    index_url = f"{repo_url.rstrip('/')}/APKINDEX.tar.gz"

    try:
        print(f"Скачивание индекса: {index_url}")
        req = urllib.request.Request(
            index_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req, timeout=15)
        tar_data = response.read()
    except urllib.error.URLError as e:
        print(f"Ошибка сети при скачивании индекса: {e}")
        return ""
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return ""

    # Распаковываем tar.gz и ищем файл APKINDEX
    try:
        with tarfile.open(fileobj=io.BytesIO(tar_data), mode="r:gz") as tar:
            for member in tar.getmembers():
                if member.name == "APKINDEX":
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        return file_obj.read().decode("utf-8")
    except tarfile.TarError as e:
        print(f"Ошибка при чтении архива индекса: {e}")

    return ""


def parse_dependencies_from_index(index_content: str, package_name: str) -> List[str]:
    """Парсит текст APKINDEX и извлекает зависимости для нужного пакета."""
    dependencies = []
    # Пакеты в индексе разделены пустыми строками
    packages = index_content.strip().split("\n\n")

    for pkg_block in packages:
        lines = pkg_block.splitlines()
        is_target_package = False

        for line in lines:
            # P: - это имя пакета
            if line.startswith("P:") and line[2:].strip() == package_name:
                is_target_package = True
            # D: - это зависимости
            elif line.startswith("D:") and is_target_package:
                deps_str = line[2:].strip()
                if deps_str:
                    # Зависимости разделены пробелами
                    deps = deps_str.split()
                    for dep in deps:
                        # Отрезаем версию (например, so:libc=1.2)
                        dep_name = dep.split("=")[0]
                        dependencies.append(dep_name)
                break  # Зависимости для этого пакета найдены, дальше не ищем

    return dependencies