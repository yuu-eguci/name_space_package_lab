import A

# *** パターン1: import A したあと A.B.C.E を参照する。 -> 参照できない。

# print(A.B.C.E)  # -> AttributeError: module 'A' has no attribute 'B'
#                 # B は名前空間パッケージとして作ったので、 AttributeError になります。

# *** パターン2: from A.B.C import D したあと A.B.C.E を参照する。 -> 参照できる。

# from A.B.C import D

# print(D)  # -> <function D at 0x101936430>
#           # わかる。
# print(E)  # NameError: name 'E' is not defined
#           # わかる。
# print(A.B.C.E)  # -> <function E at 0x1048925e0>
#                 # わからない。
#                 # from A.B.C の時点で、 import A がパワーアップするってこと???

# *** パターン3: from A.B import C したあと A.B.C.E を参照する。 -> 参照できる。

from A.B import C

# print(A.B)  # -> AttributeError: module 'A' has no attribute 'B'

from A.B import C

print(A.B)  # -> <module 'A.B' (namespace)>
            # from A.B することで A.B が参照できるようになっている。
            # なので「from A.B が import A をパワーアップさせる」という理解は、
            # 別に間違ってはいないように感じる。
