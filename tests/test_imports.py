"""README と main.py / solution.py に書いてある挙動を検証する。

import したモジュールはプロセス内でキャッシュされるので、
各ケースは別プロセスの Python で実行する。
"""

import re
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
    # repr は Python のバージョンで変わるので、名前空間かどうかは別のテストで確認する。
    assert lines[1].startswith("<module 'A.B' ")


def test_pattern4_regular_package_behaves_the_same():
    result = run('main.py', '4')

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "AttributeError: module 'xml' has no attribute 'etree'"
    assert lines[1] == "<class 'xml.etree.ElementTree.Element'>"
    assert lines[2].startswith("<module 'xml.etree' from ")


def test_pattern5_shows_sys_modules_and_parent_attribute():
    result = run('main.py', '5')

    assert result.returncode == 0, result.stderr
    assert result.stdout == '\n'.join(
        [
            "['A']",
            'False',
            "['A', 'A.B', 'A.B.C', 'A.B.C.bar', 'A.B.C.baz']",
            'A.B.C.bar',
            'True True',
            '',
        ]
    )


@pytest.mark.parametrize('args', [[], ['6'], ['1', '2']])
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


def test_from_import_imports_and_binds_submodules():
    # README の補足: import A の時点では A.B はまだ import されていない。
    # from A.B.C import D で A.B と A.B.C が import され、親の属性にセットされる。
    code = '\n'.join(
        [
            'import sys',
            'import A',
            'print("A.B" in sys.modules, hasattr(A, "B"))',
            'from A.B.C import D',
            'print("A.B" in sys.modules, "A.B.C" in sys.modules)',
            'print(A.B is sys.modules["A.B"], A.B.C is sys.modules["A.B.C"])',
        ]
    )
    result = run_code(code)

    assert result.returncode == 0, result.stderr
    assert result.stdout == 'False False\nTrue True\nTrue True\n'


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


def test_readme_covers_every_pattern():
    # README に書いてあるパターン番号が、 main.py の PATTERNS とずれていないことを確認する。
    # (CI は README の bash ブロックをそのまま実行するので、 README が合っていれば CI も合う。)
    result = run_code('import main; print(" ".join(sorted(main.PATTERNS)))')
    assert result.returncode == 0, result.stderr
    patterns = set(result.stdout.split())

    readme = (ROOT / 'README.md').read_text(encoding='utf-8')

    assert set(re.findall(r'main\.py (\d+)', readme)) == patterns


def test_readme_tree_matches_package_files():
    # README の「実験」にあるツリーに書いた .py が、 A/ 以下の実際のファイルとずれていないことを確認する。
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    tree = re.search(r'## 実験\n.*?```text\n(.*?)```', readme, re.S)
    assert tree is not None, 'README の「実験」にツリー (```text) がない'

    in_readme = set(re.findall(r'\w+\.py', tree.group(1)))
    actual = {p.name for p in (ROOT / 'A').rglob('*.py')}
    assert in_readme == actual
