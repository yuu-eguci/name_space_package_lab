# import したモジュールはプロセス内でキャッシュされ、あとのパターンの結果が変わってしまう。
# なので 1 回の実行ではパターンをひとつだけ動かす。
#   python main.py 1
#   python main.py 2
#   python main.py 3
#   python main.py 4

import argparse


def pattern1():
    # *** パターン1: import A したあと A.B.C.E を参照する。 -> 参照できない。
    import A

    try:
        print(A.B.C.E)
    except AttributeError as e:
        # -> AttributeError: module 'A' has no attribute 'B'
        # import A だけでは A.B はまだ import されていないので、 AttributeError になります。
        print(f'AttributeError: {e}')


def pattern2():
    # *** パターン2: from A.B.C import D したあと A.B.C.E を参照する。 -> 参照できる。
    import A
    from A.B.C import D

    print(D)  # -> <function D at 0x101936430>
    # わかる。

    try:
        print(E)
    except NameError as e:
        # -> NameError: name 'E' is not defined
        # わかる。
        print(f'NameError: {e}')

    print(A.B.C.E)  # -> <function E at 0x1048925e0>
    # わからない。
    # from A.B.C の時点で、 import A がパワーアップするってこと???
    # -> from A.B.C import D は A, A.B, A.B.C を順に import し、
    #    そのとき A.B を A の属性に、 A.B.C を A.B の属性にセットする。
    #    なので A.B.C.E がたどれるようになる。 (README の補足を参照)


def pattern3():
    # *** パターン3: from A.B import C したあと A.B を参照する。 -> 参照できる。
    import A
    from A.B import C

    print(C)  # -> <module 'A.B.C' from '.../A/B/C/__init__.py'>
    print(A.B)  # -> <module 'A.B' (namespace) from ['.../A/B']>
    # (↑は 3.12 以降の表示。 3.11 では NamespaceLoader オブジェクトの表示になる。)
    # from A.B することで A.B が参照できるようになっている。
    # なので「from A.B が import A をパワーアップさせる」という理解は、
    # 別に間違ってはいないように感じる。


def pattern4():
    # *** パターン4: __init__.py のある通常のパッケージ (標準ライブラリの xml) でも同じことが起きる。
    import xml

    try:
        print(xml.etree)
    except AttributeError as e:
        # -> AttributeError: module 'xml' has no attribute 'etree'
        # import xml だけでは xml.etree はまだ import されていない。パターン1と同じ。
        print(f'AttributeError: {e}')

    from xml.etree.ElementTree import Element

    print(Element)  # -> <class 'xml.etree.ElementTree.Element'>
    print(xml.etree)  # -> <module 'xml.etree' from '.../xml/etree/__init__.py'>
    # from xml.etree.ElementTree で xml.etree が import され、 xml の属性にセットされた。
    # 名前空間パッケージ特有の挙動ではない、ということ。


PATTERNS = {'1': pattern1, '2': pattern2, '3': pattern3, '4': pattern4}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='名前空間パッケージの import 実験')
    parser.add_argument('pattern', choices=PATTERNS, help='実行するパターン番号')
    PATTERNS[parser.parse_args().pattern]()
