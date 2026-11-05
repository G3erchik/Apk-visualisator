"""Module for extracting dependencies from APK packages."""

import io
import tarfile
import urllib.error
import urllib.request
from typing import List


def fetch_apk_metadata(repo_url: str, package_name: str) -> str:
    """Downloads the APK package by URL and returns .PKGINFO contents."""
    if repo_url.endswith(".apk"):
        apk_url = repo_url
    else:
        apk_url = f"{repo_url.rstrip('/')}/{package_name}.apk"

    try:
        print(f"Скачивание: {apk_url}")
        req = urllib.request.Request(
            apk_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req, timeout=15)
        apk_data = response.read()
    except urllib.error.URLError as e:
        print(f"Ошибка сети при скачивании: {e}")
        return ""
    except Exception as e:
        print(f"Неизвестная ошибка при скачивании: {e}")
        return ""

    try:
        with tarfile.open(fileobj=io.BytesIO(apk_data), mode="r:gz") as tar:
            for member in tar.getmembers():
                if member.name == ".PKGINFO":
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        return file_obj.read().decode("utf-8")
    except tarfile.TarError as e:
        print(f"Ошибка при чтении архива APK: {e}")

    return ""


def parse_dependencies(pkginfo_content: str) -> List[str]:
    """Parses .PKGINFO text and extracts the list of dependencies."""
    dependencies = []
    for line in pkginfo_content.splitlines():
        if line.startswith("depend = "):
            dep = line[9:].strip()
            dep_name = dep.split("=")[0]
            dependencies.append(dep_name)
    return dependencies