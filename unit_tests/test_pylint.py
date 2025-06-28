from pathlib import Path
import pytest
import pytest_check
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from io import StringIO

SRC = Path(__file__).parents[1] / "src"


@pytest.mark.parametrize("file_path", SRC.rglob("*.py"),
                         ids=lambda p: f'{p.parent.name}-{p.stem}')
def test_pylint_src(file_path: Path) -> None:
    """Run pylint on all Python files in the src/ directory."""
    # Run pylint on all files and fail if pylint returns nonzero exit code
    assert file_path.is_file(), f"File {file_path} does not exist"
    output = StringIO()
    reporter = TextReporter(output)
    result = Run([str(file_path)], reporter=reporter, exit=False)
    output.seek(0)
    lines = output.getvalue().splitlines()
    score_line = [line for line in lines
                  if "Your code has been rated at" in line]
    assert score_line, "Could not find pylint score line"
    score_str = score_line[0].split(" at ")[1].split("/")[0].strip()
    score = float(score_str)
    pytest_check.equal(score, 10.0, f"pylint score for {file_path} is {score}")
    for line in lines:
        if file_path.name in line:
            err = line.split(file_path.name)[-1].strip(':').strip()
            pytest_check.fail(err)
