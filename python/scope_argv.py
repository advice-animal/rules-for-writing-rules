import sys
from pathlib import Path

import libcst as cst
from fixit import LintRule
from fixit.api import LintRunner, generate_config
from libcst.metadata import QualifiedNameProvider


class _ArgvClassifier(LintRule):
    # Priority: multiple > single > zero > unknown
    METADATA_DEPENDENCIES = (QualifiedNameProvider, *LintRule.METADATA_DEPENDENCIES)

    def __init__(self) -> None:
        super().__init__()
        self.result = 'unknown'

    def visit_Subscript(self, node: cst.Subscript) -> None:
        qnames = self.get_metadata(QualifiedNameProvider, node.value, set())
        if not any(qn.name == 'sys.argv' for qn in qnames):
            return

        if len(node.slice) != 1:
            self.result = 'multiple'
            return

        s = node.slice[0].slice
        if isinstance(s, cst.Slice):
            self.result = 'multiple'
        elif isinstance(s, cst.Index) and isinstance(s.value, cst.Integer):
            if s.value.value == '0' and self.result == 'unknown':
                self.result = 'zero'
            elif s.value.value == '1' and self.result != 'multiple':
                self.result = 'single'
            else:
                self.result = 'multiple'
        else:
            self.result = 'multiple'


def classify_argv(path: str) -> str:
    src = Path(path).read_bytes()
    try:
        cst.parse_module(src)
    except cst.ParserSyntaxError:
        return 'unknown'
    config = generate_config(Path(path))
    classifier = _ArgvClassifier()
    list(LintRunner(Path(path), src).collect_violations([classifier], config))
    return classifier.result


def main() -> None:
    for path in sys.argv[1:]:
        print(f'{path}: {classify_argv(path)}')


if __name__ == '__main__':
    main()
