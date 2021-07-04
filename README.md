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

### なんでやねん、ってならない方

教えてくださいなんでなんですか……。

## 実験

Code A も Code B もどちらも再現するコードを自分で作ってみて、 keras 特有の現象なのか普通に Python の仕様なのか調べる。

```python
# シンプルにこう置き換えて再現する。
import A
from A.B.C import D

print(A.B.C.E)
```

## 実験結果

main.py をご覧あれ。
