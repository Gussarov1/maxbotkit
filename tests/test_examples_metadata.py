from pathlib import Path


def test_examples_have_module_docstrings() -> None:
    root = Path("examples")
    example_files = sorted(root.glob("*/*.py"))

    assert example_files
    for path in example_files:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith('"""')
