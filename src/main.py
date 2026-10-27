"""Модуль для CLI-инструмента визуализации зависимостей (Этап 3)."""

import argparse
import sys

from apk_parser import fetch_apk_metadata, parse_dependencies
from graph_builder import DependencyGraph


def parse_arguments() -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей Alpine Linux (apk)"
    )
    parser.add_argument(
        "-p", "--package", required=True, help="Имя анализируемого пакета"
    )
    parser.add_argument(
        "-r", "--repo", required=True,
        help="URL репозитория или путь к тестовому файлу"
    )
    parser.add_argument(
        "-t", "--test-mode", action="store_true",
        help="Режим работы с тестовым репозиторием"
    )
    parser.add_argument(
        "-o", "--output", default="graph.png",
        help="Имя файла для сохранения графа"
    )
    parser.add_argument(
        "-a", "--ascii", action="store_true",
        help="Вывод зависимостей в формате ASCII-дерева"
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> bool:
    """Валидация параметров (обработка ошибок)."""
    if not args.package.replace('-', '').isalnum():
        print("Ошибка: Некорректное имя пакета.", file=sys.stderr)
        return False
    if not args.output.endswith(('.png', '.svg')):
        print("Ошибка: Файл графа должен быть .png или .svg", file=sys.stderr)
        return False
    return True


def print_config(args: argparse.Namespace) -> None:
    """Выводит настройки в формате ключ-значение."""
    print("--- Конфигурация ---")
    print(f"Package: {args.package}")
    print(f"Repository: {args.repo}")
    print(f"Test Mode: {args.test_mode}")
    print(f"Output File: {args.output}")
    print(f"ASCII Tree: {args.ascii}")
    print("--------------------")


def main() -> None:
    """Точка входа в приложение."""
    args = parse_arguments()
    if not validate_args(args):
        sys.exit(1)

    print_config(args)

    # Создаем объект графа
    graph = DependencyGraph()

    # Если включен тестовый режим (Этап 3)
    if args.test_mode:
        print(f"\nЗагрузка тестового графа из файла: {args.repo}")
        graph.load_from_test_file(args.repo)

        # Проверяем, есть ли вообще такой пакет в графе
        if args.package not in graph.graph and args.package not in [
            child for children in graph.graph.values() for child in children
        ]:
            print(f"Пакет '{args.package}' не найден в тестовом графе.")
            return

        # Запускаем обход BFS для проверки работоспособности (и сбора visited)
        visited = graph.build_bfs_with_recursion(args.package)
        print(f"Посещено пакетов при обходе BFS: {len(visited)}")

        # Выводим ASCII-дерево, если передан флаг -a
        if args.ascii:
            graph.print_ascii_tree(args.package)
        else:
            print("Граф загружен. Используйте флаг -a для вывода дерева.")

    else:
        # Реальный режим (Этап 2)
        print(f"\nПолучение прямых зависимостей для '{args.package}'...")
        metadata = fetch_apk_metadata(args.repo, args.package)

        if not metadata:
            print("Не удалось получить метаданные пакета.")
            return

        deps = parse_dependencies(metadata)
        print(f"Найдено прямых зависимостей: {len(deps)}")
        for dep in deps:
            print(f" - {dep}")


if __name__ == "__main__":
    main()