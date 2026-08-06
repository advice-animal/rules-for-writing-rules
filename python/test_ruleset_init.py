from .ruleset_init import check_ruleset_dirs, collect_imported_names, find_ruleset_dirs


def test_collect_imported_names(tmp_path):
    (tmp_path / "a.py").write_text("import os\nfrom pathlib import Path\n")
    (tmp_path / "b.py").write_text("import libcst.metadata\nfrom . import c\n")
    assert collect_imported_names(tmp_path) == {"os", "pathlib", "libcst"}


def test_collect_imported_names_skips_tests_dir(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "a.py").write_text("import os\n")
    assert collect_imported_names(tmp_path) == set()


def test_find_ruleset_dirs(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "ick.toml").write_text('[[rule]]\nname = "x"\nimpl = "python"\n')
    other = tmp_path / "other"
    other.mkdir()
    (other / "ick.toml").write_text('[[rule]]\nname = "y"\nimpl = "not_python"\n')
    assert find_ruleset_dirs(tmp_path) == {pkg}


def test_find_ruleset_dirs_skips_tests_dir(tmp_path):
    tests_pkg = tmp_path / "tests" / "pkg"
    tests_pkg.mkdir(parents=True)
    (tests_pkg / "ick.toml").write_text('[[rule]]\nname = "x"\nimpl = "python"\n')
    assert find_ruleset_dirs(tmp_path) == set()


def _make_ruleset_dir(tmp_path, name):
    pkg = tmp_path / name
    pkg.mkdir()
    (pkg / "ick.toml").write_text('[[rule]]\nname = "x"\nimpl = "python"\n')
    (pkg / "x.py").write_text("")
    return pkg


def test_check_ruleset_dirs_ok(tmp_path):
    pkg = _make_ruleset_dir(tmp_path, "goodpkg")
    (pkg / "__init__.py").write_text("")
    assert check_ruleset_dirs(tmp_path) == 0


def test_check_ruleset_dirs_missing_init(tmp_path):
    pkg = _make_ruleset_dir(tmp_path, "goodpkg")
    assert check_ruleset_dirs(tmp_path) == 0
    assert (pkg / "__init__.py").read_text() == ""


def test_check_ruleset_dirs_nonempty_init(tmp_path):
    pkg = _make_ruleset_dir(tmp_path, "goodpkg")
    (pkg / "__init__.py").write_text("x = 1\n")
    assert check_ruleset_dirs(tmp_path) == 99


def test_check_ruleset_dirs_stdlib_name_collision(tmp_path):
    pkg = _make_ruleset_dir(tmp_path, "json")
    (pkg / "__init__.py").write_text("")
    assert check_ruleset_dirs(tmp_path) == 99


def test_check_ruleset_dirs_imported_name_collision(tmp_path):
    pkg = _make_ruleset_dir(tmp_path, "libcst")
    (pkg / "__init__.py").write_text("")
    other = tmp_path / "other"
    other.mkdir()
    (other / "uses_libcst.py").write_text("import libcst\n")
    assert check_ruleset_dirs(tmp_path) == 99
