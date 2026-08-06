import pytest
from .scope_argv import classify_argv


@pytest.mark.parametrize('src,expected', [
    ('import sys\nx = sys.argv[1]', 'single'),
    ('import sys\nx = sys.argv[1:]', 'multiple'),
    ('import sys\nprint(sys.argv)', 'unknown'),
    ('import sys as bar\nx = bar.argv[1]', 'single'),
    ('import sys as bar\nx = bar.argv[1:]', 'multiple'),
    ('import sys as bar\nprint(bar.argv)', 'unknown'),
    ('from sys import argv\nx = argv[1]', 'single'),
    ('from sys import argv\nx = argv[1:]', 'multiple'),
    ('from sys import argv\nprint(argv)', 'unknown'),
    ('from sys import argv as args\nx = args[1]', 'single'),
    ('import sys\nx = sys.argv[0]', 'zero'),
    ('import sys\nx = sys.argv[0]\ny = sys.argv[1]', 'single'),
    ('import sys\nx = sys.argv[0]\ny = sys.argv[1:]', 'multiple'),
])
def test_classify_argv(tmp_path, src, expected):
    f = tmp_path / 'test.py'
    f.write_text(src)
    assert classify_argv(str(f)) == expected
