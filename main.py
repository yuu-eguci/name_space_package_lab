import A

# print(A.B.C.E)  # -> AttributeError: module 'A' has no attribute 'B'
#                 # B は名前空間パッケージとして作ったので、 AttributeError になります。

# ***

# C は普通のパッケージです。中に D と E があります。
# from A.B import C

# print(C.D)  # -> <function D at 0x107606430>
#             # わかる。
# print(C.E)  # -> <function E at 0x1076065e0>
#             # わかる。
# print(A.B.C.E)  # -> <function E at 0x1076065e0>
#                 # わからない。
#                 # from A.B の時点で、 import A がパワーアップするってこと???

# ***

from A.B.C import D

print(D)  # -> <function D at 0x101936430>
          # わかる。
# print(E)  # NameError: name 'E' is not defined
#           # わかる。
print(A.B.C.E)  # -> <function E at 0x1048925e0>
                # わからない。
                # from A.B.C の時点で、 import A がパワーアップするってこと???
