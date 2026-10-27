"""Модуль для построения и обхода графа зависимостей."""

from collections import deque
from typing import Dict, List, Set


class DependencyGraph:
    """Класс для хранения и обхода графа зависимостей."""

    def __init__(self) -> None:
        # Словарь: Ключ - пакет, Значение - список его прямых зависимостей
        self.graph: Dict[str, List[str]] = {}

    def add_edge(self, parent: str, child: str) -> None:
        """Добавляет ребро в граф (родитель -> зависимость)."""
        if parent not in self.graph:
            self.graph[parent] = []
        self.graph[parent].append(child)

    def load_from_test_file(self, file_path: str) -> None:
        """Загружает граф из тестового файла (формат: A -> B)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if '->' in line:
                        parts = line.split('->')
                        parent = parts[0].strip()
                        child = parts[1].strip()
                        if parent and child:
                            self.add_edge(parent, child)
        except FileNotFoundError:
            print(f"Ошибка: Файл {file_path} не найден.")
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")

    def build_bfs_with_recursion(self, start_package: str) -> Set[str]:
        """Строит граф с помощью BFS с рекурсией (обход в ширину).

        Возвращает множество всех посещенных пакетов.
        """
        visited: Set[str] = set()

        # Внутренняя рекурсивная функция для обхода
        def bfs_recursive(queue: deque) -> None:
            if not queue:
                return  # Базовый случай рекурсии: очередь пуста

            current_pkg = queue.popleft()

            # Если уже посещали этот пакет, пропускаем (защита от циклов)
            if current_pkg in visited:
                return bfs_recursive(queue)

            visited.add(current_pkg)

            # Получаем зависимости для текущего пакета
            dependencies = self.graph.get(current_pkg, [])

            for dep in dependencies:
                if dep not in visited:
                    queue.append(dep)

            # Рекурсивный вызов для следующего элемента очереди
            bfs_recursive(queue)

        # Запускаем рекурсию
        initial_queue = deque([start_package])
        bfs_recursive(initial_queue)

        return visited

    def print_ascii_tree(self, start_package: str) -> None:
        """Выводит граф в виде ASCII-дерева в консоль."""
        print(f"\nASCII-дерево для пакета '{start_package}':")
        visited = set()
        self._print_tree_recursive(start_package, "", True, visited)

    def _print_tree_recursive(
            self, package: str, prefix: str, is_last: bool, visited: Set[str]
    ) -> None:
        """Рекурсивная функция для отрисовки веток дерева."""
        # Защита от циклов при отрисовке
        if package in visited:
            print(f"{prefix}{'└── ' if is_last else '├── '}{package} (цикл)")
            return

        visited.add(package)

        # Рисуем текущий узел
        connector = '└── ' if is_last else '├── '
        print(f"{prefix}{connector}{package}")

        # Получаем детей
        children = self.graph.get(package, [])
        if not children:
            return

        # Вычисляем префикс для детей
        child_prefix = prefix + ('    ' if is_last else '│   ')

        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_tree_recursive(
                child, child_prefix, is_last_child, visited
            )