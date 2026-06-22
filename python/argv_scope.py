"""Ick rule: check that each rule's argv usage matches its scope.

File-scoped rules receive filenames via sys.argv and should be "multiple".
Project/repo-scoped rules receive no filenames and should be "zero" or "unknown".
"""
import sys
import tomllib
from pathlib import Path

from .scope_argv import classify_argv

EXPECTED = {
    'file': {'multiple'},
    'project': {'zero', 'unknown'},
    'repo': {'zero', 'unknown'},
}


def check_toml(toml_path):
    rules = tomllib.loads(toml_path.read_text()).get('rule', [])
    exit_code = 0
    for rule in rules:
        if rule.get('impl') != 'python':
            continue
        scope = rule.get('scope')
        if scope not in EXPECTED:
            continue
        py_path = toml_path.parent / f'{rule["name"]}.py'
        if not py_path.exists():
            continue
        actual = classify_argv(str(py_path))
        expected = EXPECTED[scope]
        if scope == 'file' and rule.get('batch_size') == 1:
            expected = expected | {'single'}
        if actual not in expected:
            print(f'{py_path}: scope={scope!r} expects {expected}, got {actual!r}')
            exit_code = 99
    return exit_code


def main():
    exit_code = 0
    for toml_path in Path(".").glob("**/ick.toml"):
        result = check_toml(toml_path)
        if result == 99:
            exit_code = 99
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
