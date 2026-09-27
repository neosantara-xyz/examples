#!/usr/bin/env python3
import ast
import json
import sys
from pathlib import Path


def code_errors(notebook: dict) -> list[str]:
    """
    Return syntax problems in the notebook's code cells.

    - Every code cell must parse as Python once IPython lines (`!cmd`, `%magic`) are removed.
    - Source lines must not end with a literal backslash-n (a JSON escaping mistake that
      collapses the whole cell into one line in Colab).
    """
    errors = []
    code_index = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        code_index += 1
        source = cell.get("source", [])
        lines = source if isinstance(source, list) else [source]

        for line in lines:
            if line.endswith("\\n"):
                errors.append(f"code cell {code_index}: literal '\\n' instead of a newline")
                break

        python = "".join(
            line for line in lines if not line.lstrip().startswith(("!", "%"))
        )
        try:
            ast.parse(python)
        except SyntaxError as e:
            errors.append(f"code cell {code_index}, line {e.lineno}: {e.msg}")
    return errors


def validate_notebooks(directory="cookbook"):
    """
    Recursively finds all .ipynb files in the given directory and checks that
    each one is valid JSON and that every code cell is valid Python.
    """
    error_count = 0
    file_count = 0

    cookbook_path = Path(directory)

    if not cookbook_path.exists():
        print(f"Error: Directory '{directory}' not found.")
        sys.exit(1)

    print(f"🔍 Validating JSON and Python syntax for all notebooks in '{directory}/'...")
    print("-" * 60)

    for ipynb_file in sorted(cookbook_path.rglob("*.ipynb")):
        file_count += 1
        try:
            with open(ipynb_file, "r", encoding="utf-8") as f:
                notebook = json.load(f)
        except json.JSONDecodeError as e:
            error_count += 1
            print(f"❌ FAIL: {ipynb_file}")
            print(f"   Reason: invalid JSON: {e}")
            continue
        except Exception as e:
            error_count += 1
            print(f"❌ ERROR: Could not read {ipynb_file}")
            print(f"   Reason: {e}")
            continue

        problems = code_errors(notebook)
        if problems:
            error_count += 1
            print(f"❌ FAIL: {ipynb_file}")
            for problem in problems:
                print(f"   Reason: {problem}")
        else:
            print(f"✅ PASS: {ipynb_file}")

    print("-" * 60)
    if error_count == 0:
        print(f"🎉 Success! {file_count} notebooks validated. No errors found.")
        return True
    else:
        print(f"⚠️  Found {error_count} failing notebooks out of {file_count}.")
        return False


if __name__ == "__main__":
    success = validate_notebooks()
    if not success:
        sys.exit(1)
