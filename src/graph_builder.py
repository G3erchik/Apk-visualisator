"""Module for building and traversing the dependency graph."""

from collections import deque
from typing import Dict, List, Set


class DependencyGraph:
    """Class for storing and traversing the dependency graph."""

    def __init__(self) -> None:
        """Initializes an empty graph."""
        self.graph: Dict[str, List[str]] = {}

    def add_edge(self, parent: str, child: str) -> None:
        """Adds an edge to the graph."""
        if parent not in self.graph:
            self.graph[parent] = []
        self.graph[parent].append(child)

    def load_from_test_file(self, file_path: str) -> None:
        """Loads the graph from a test file (format: A -> B)."""
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
        """Builds the graph using BFS with recursion."""
        visited: Set[str] = set()

        def bfs_recursive(queue: deque) -> None:
            """Recursive BFS function."""
            if not queue:
                return

            current_pkg = queue.popleft()

            if current_pkg in visited:
                return bfs_recursive(queue)

            visited.add(current_pkg)

            dependencies = self.graph.get(current_pkg, [])
            for dep in dependencies:
                if dep not in visited:
                    queue.append(dep)

            bfs_recursive(queue)

        initial_queue = deque([start_package])
        bfs_recursive(initial_queue)

        return visited

    def print_ascii_tree(self, start_package: str) -> None:
        """Prints the graph as an ASCII tree."""
        print(f"\nASCII-дерево для пакета '{start_package}':")
        visited = set()
        self._print_tree_recursive(start_package, "", True, visited)

    def _print_tree_recursive(
            self, package: str, prefix: str, is_last: bool, visited: Set[str]
    ) -> None:
        """Recursive function for drawing tree branches."""
        if package in visited:
            connector = '└── ' if is_last else '├── '
            print(f"{prefix}{connector}{package} (цикл)")
            return

        visited.add(package)

        connector = '└── ' if is_last else '├── '
        print(f"{prefix}{connector}{package}")

        children = self.graph.get(package, [])
        if not children:
            return

        child_prefix = prefix + ('    ' if is_last else '│   ')

        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_tree_recursive(
                child, child_prefix, is_last_child, visited
            )