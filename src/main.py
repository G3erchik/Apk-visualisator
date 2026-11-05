"""Module for CLI dependency visualization tool (Stages 1-4)."""

import argparse
import sys

# Импорты для Этапа 2
from apk_parser import fetch_apkindex, parse_dependencies_from_index
# Импорт для Этапов 3 и 4
from graph_builder import DependencyGraph


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей Alpine Linux (apk)"
    )
    parser.add_argument("-p", "--package", required=True, help="Имя пакета")
    parser.add_argument("-r", "--repo", required=True, help="URL или файл")
    parser.add_argument("-t", "--test-mode", action="store_true", help="Тест")
    parser.add_argument("-o", "--output", default="graph.png", help="Файл")
    parser.add_argument("-a", "--ascii", action="store_true", help="ASCII")
    # Новый флаг для Этапа 4
    parser.add_argument(
        "--reverse", action="store_true",
        help="Поиск обратных зависимостей (Этап 4)"
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> bool:
    """Validates arguments (error handling)."""
    if not args.package.replace('-', '').isalnum():
        print("Ошибка: Некорректное имя пакета.", file=sys.stderr)
        return False
    if not args.output.endswith(('.png', '.svg')):
        print("Ошибка: Файл графа должен быть .png или .svg", file=sys.stderr)
        return False
    return True


def print_config(args: argparse.Namespace) -> None:
    """Prints settings in key-value format."""
    print("--- Конфигурация ---")
    print(f"Package: {args.package}")
    print(f"Repository: {args.repo}")
    print(f"Test Mode: {args.test_mode}")
    print(f"Output File: {args.output}")
    print(f"ASCII Tree: {args.ascii}")
    print(f"Reverse Mode: {args.reverse}")
    print("--------------------")


def display_direct_dependencies(repo_url: str, package_name: str) -> None:
    """Displays direct dependencies (Stage 2) via APKINDEX."""
    print(f"\nПолучение прямых зависимостей для '{package_name}'...")

    index_content = fetch_apkindex(repo_url)

    if not index_content:
        print("Не удалось получить индекс пакетов.")
        return

    deps = parse_dependencies_from_index(index_content, package_name)

    if not deps:
        print(f"Пакет '{package_name}' не найден в индексе или нет зависимостей.")
        return

    print(f"Найдено прямых зависимостей: {len(deps)}")
    for dep in deps:
        print(f" - {dep}")


def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    if not validate_args(args):
        sys.exit(1)

    print_config(args)
    graph = DependencyGraph()

    if args.test_mode:
        print(f"\nЗагрузка тестового графа из файла: {args.repo}")
        graph.load_from_test_file(args.repo)

        # Логика Этапа 4: Обратные зависимости
        if args.reverse:
            print(f"\nПоиск обратных зависимостей для '{args.package}'...")
            rev_deps = graph.find_reverse_dependencies(args.package)

            if not rev_deps:
                print("Обратных зависимостей не найдено.")
            else:
                print(f"Найдено обратных зависимостей: {len(rev_deps)}")
                for dep in rev_deps:
                    print(f" - {dep}")

        # Логика Этапа 3: Обычный обход BFS и ASCII
        else:
            visited = graph.build_bfs_with_recursion(args.package)
            print(f"Посещено пакетов при обходе BFS: {len(visited)}")
            if args.ascii:
                graph.print_ascii_tree(args.package)
    else:
        # Реальный режим (Этап 2)
        display_direct_dependencies(args.repo, args.package)


if __name__ == "__main__":
    main()