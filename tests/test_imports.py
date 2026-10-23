"""README と main.py / solution.py に書いてある挙動を検証する。

import したモジュールはプロセス内でキャッシュされるので、
各ケースは別プロセスの Python で実行する。
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def run_code(code):
    # -c のときは cwd が sys.path に入るので、 A パッケージを import できる。
    return run('-c', code)


def test_pattern1_attribute_error():
    result = run('main.py', '1')

    assert result.returncode == 0, result.stderr
    assert result.stdout == "AttributeError: module 'A' has no attribute 'B'\n"


def test_pattern2_from_import_binds_submodules():
    result = run('main.py', '2')

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0].startswith('<function D at ')
    assert lines[1] == "NameError: name 'E' is not defined"
    assert lines[2].startswith('<function E at ')


def test_pattern3_from_import_binds_namespace_package():
    result = run('main.py', '3')

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0].startswith("<module 'A.B.C' from ")
    assert lines[1].startswith("<module 'A.B' (namespace)")


@pytest.mark.parametrize('args', [[], ['4'], ['1', '2']])
def test_main_rejects_invalid_arguments(args):
    result = run('main.py', *args)

    assert result.returncode == 2
    assert 'usage:' in result.stderr


def test_solution():
    result = run('solution.py')

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0].startswith('<function D at ')
    assert lines[1].startswith('<function E at ')


def test_import_function_as_module_fails():
    result = run_code('import A.B.C.D')

    assert result.returncode == 1
    assert "ModuleNotFoundError: No module named 'A.B.C.D'" in result.stderr


def test_A_and_B_are_namespace_packages():
    result = run_code(
        'import A.B.C; print(A.__file__, A.B.__file__, A.B.C.__file__ is None)'
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == 'None None False\n'


def test_same_behavior_with_regular_package():
    # 名前空間パッケージ特有ではないことを、通常のパッケージ (xml) で確かめる。
    code = '\n'.join(
        [
            'import xml',
            'print(hasattr(xml, "etree"))',
            'from xml.etree.ElementTree import Element',
            'print(hasattr(xml, "etree"))',
        ]
    )
    result = run_code(code)

    assert result.returncode == 0, result.stderr
    assert result.stdout == 'False\nTrue\n'
