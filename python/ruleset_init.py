"""Ick rule: make sure each rule package directory is a proper, safe package.

Rule scripts are run as `python -m <dir>.<rule_name>` with the ruleset root on
PYTHONPATH, so the directory holding a rule's ick.toml is imported as a Python
package. It must have an empty __init__.py (created here if missing), and its
name must not shadow a stdlib module or a module that some rule actually
imports.
"""
import ast
import sys
import tomllib
from pathlib import Path


def collect_imported_names(root):
    names = set()
    for py_path in root.glob("**/*.py"):
        if "tests" in py_path.parts:
            continue
        try:
            tree = ast.parse(py_path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    names.add(node.module.split(".")[0])
    return names


def find_ruleset_dirs(root):
    dirs = set()
    for toml_path in root.glob("**/ick.toml"):
        if "tests" in toml_path.parts:
            continue
        rules = tomllib.loads(toml_path.read_text()).get("rule", [])
        if any(rule.get("impl") == "python" for rule in rules):
            dirs.add(toml_path.parent)
    return dirs


def check_ruleset_dirs(root):
    exit_code = 0
    imported_names = collect_imported_names(root)
    for ruleset_dir in sorted(find_ruleset_dirs(root)):
        name = ruleset_dir.name
        init_py = ruleset_dir / "__init__.py"
        if not init_py.exists():
            init_py.write_text("")
        elif init_py.read_text().strip():
            print(f"{init_py}: should be empty")
            exit_code = 99
        if name in sys.stdlib_module_names:
            print(f"{ruleset_dir}: name {name!r} shadows stdlib module {name!r}")
            exit_code = 99
        elif name in imported_names:
            print(f"{ruleset_dir}: name {name!r} shadows imported module {name!r}")
            exit_code = 99
    return exit_code


def main():
    sys.exit(check_ruleset_dirs(Path(".")))


if __name__ == "__main__":
    main()
