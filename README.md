Name space package lab
===

`import A` だけでは `A.B.C.E` を参照できないのに、 `from A.B.C import D` をはさむと参照できるようになる。この挙動を再現して確かめるリポジトリ。

- Docker: 対応!
- Python: 3.14 (Docker イメージ) / 3.11〜3.15 で CI 確認
- Lint: [Ruff](https://docs.astral.sh/ruff/) (`ruff check` / `ruff format --check`)
- Test: [pytest](https://docs.pytest.org/)

## パッと実行してみたい

```bash
docker build -t name-space-package-lab .

# 実験 (パターン 1〜4) と解消方法
docker run --rm name-space-package-lab python main.py 1
docker run --rm name-space-package-lab python main.py 2
docker run --rm name-space-package-lab python main.py 3
docker run --rm name-space-package-lab python main.py 4
docker run --rm name-space-package-lab python solution.py

# lint とテスト
docker run --rm name-space-package-lab ruff check .
docker run --rm name-space-package-lab ruff format --check .
docker run --rm name-space-package-lab pytest
```

Docker なしで動かす場合 (Python 3.11 以上) はこう。 `main.py` と `solution.py` は標準ライブラリだけで動くので、 lint とテストをしないならインストール不要。

```bash
python3 main.py 1

python3 -m venv .venv
. .venv/bin/activate
pip install --require-hashes -r requirements-dev.txt
ruff check . && ruff format --check . && pytest
```

GitHub Actions でも、 Docker 上の lint・テストと、 Python 3.11〜3.15 でのテストを実行する。

## 謎現象

keras のコードを書いているとき、 import の順序で参照できる属性が変わる現象に出会った。以下は当時のコード例。現在の keras での再現は確認していない。

- これ↓は Attribute エラー。

```python
# Code A

import keras
# from keras.preprocessing.image import img_to_array

print(keras.preprocessing.image.load_img)  # -> AttributeError: module 'keras' has no attribute 'preprocessing'
                                           # -> わかる。エラーではあるがよくあるやつ。
```

- これ↓は通る。

```python
# Code B

import keras
from keras.preprocessing.image import img_to_array

print(keras.preprocessing.image.load_img)  # -> <function load_img at 0x15c0cb5e0>
                                           # -> なんでやねん。
```

## 実験

![init](https://user-images.githubusercontent.com/28250432/124377464-0424aa80-dce7-11eb-83f9-f53d1c1ecc30.png)

Code A も Code B もどちらも再現するコードを自分で作ってみて、 keras 特有の現象なのか普通に Python の仕様なのか調べる。

```python
# シンプルにこう置き換えて再現する。
import A
from A.B.C import D

print(A.B.C.E)
```

`A` と `A/B` は `__init__.py` のない名前空間パッケージ、 `A/B/C` は `__init__.py` のある通常のパッケージ。

## 実験結果

[main.py](main.py) で確かめられる。 `python main.py <パターン番号>` で各パターンを実行できる。

| コマンド | やること | 結果 |
| --- | --- | --- |
| `python main.py 1` | `import A` したあと `A.B.C.E` を参照 | `AttributeError` |
| `python main.py 2` | `from A.B.C import D` したあと `A.B.C.E` を参照 | 参照できる (`E` 単体は `NameError`) |
| `python main.py 3` | `from A.B import C` したあと `A.B` を参照 | 参照できる |
| `python main.py 4` | 通常のパッケージ `xml` で同じことをする (補足を参照) | `import xml` だけだと `AttributeError`、 `from xml.etree.ElementTree import ...` のあとは参照できる |

import したモジュールはプロセス内でキャッシュされるため、パターンは 1 回の実行につきひとつだけ動かす。

- 再現した。
- よって keras 特有の現象ではなく、自分でパッケージを作っても発生する。
- すごいわかりづらい仕様で Python らしくないと感じるので、ほかの Pythonista 諸兄がどう感じるのか気になる。

### 補足: 名前空間パッケージ特有の仕様ではない

`import A` の時点で `A` 自体はロードされている。 `A.B` を参照できないのは、まだ `A.B` が import されていないから。

Python では、サブモジュールを import すると、そのサブモジュールが親パッケージの属性としてセットされる ([The import system - Submodules](https://docs.python.org/3/reference/import.html#submodules))。 `from A.B.C import D` は `A`、 `A.B`、 `A.B.C` を順に import するので、その副作用で `A.B` と `A.B.C` が属性としてセットされ、 `A.B.C.E` が参照できるようになる。

これは `__init__.py` のある通常のパッケージでも同じ。たとえば標準ライブラリの `xml` でも起きる。

```python
import xml

# print(xml.etree)  # -> AttributeError: module 'xml' has no attribute 'etree'

from xml.etree.ElementTree import Element

print(xml.etree)  # -> <module 'xml.etree' from '...'>
```

`python main.py 4` で同じことを動かして確かめられる。

当時の keras の例も、子モジュールの import によって親パッケージの属性が追加されたと考えられる。

### 「すごいわかりづらい」の解消方法

[solution.py](solution.py) のように、使うパッケージを直接 import すればいい。

```python
import A.B.C

print(A.B.C.E)
```

BEAUTIFUL...

## 開発メモ

`requirements-dev.txt` は `requirements-dev.in` から生成した、ハッシュ付きのロックファイル。更新するときはこう。

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/work -w /work python:3.14-slim sh -c \
  "pip install -q --user uv==0.13.5 && python -m uv pip compile --universal --python-version 3.11 --generate-hashes requirements-dev.in -o requirements-dev.txt"
```

uv のバージョンは固定している。ホスト側と同じユーザー ID・グループ ID で実行するので、生成したファイルが root 所有にならない。

`Dockerfile` のベースイメージは digest で固定している。 Python を上げるときは、タグと digest をあわせて更新する。
