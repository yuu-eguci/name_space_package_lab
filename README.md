Name space package lab
===

⚗️ keras コードを書いているとき、謎現象が発生しました。その現象を再現、実験するために作ったリポジトリです。

## 謎現象

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

## 実験結果

[main.py](main.py) をご覧あれ。

- 再現した。
- よって keras 特有の現象ではなく、自分でパッケージを作っても発生する。
- 今の所「名前空間パッケージ下のパッケージをひとつ import する(`from A.B.C import D`)ことで名前空間パッケージがようやくロードされ、 `import A` が**パワーアップして** `A.B.C.E` が使えるようになる……?」というのが実感。
- ともあれ、すごいわかりづらい仕様で Python らしくないと感じるので、ほかの Pythonista 諸兄がどう感じるのか気になる。
