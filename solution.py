# SOLUTION: この import の仕方であれば、下記問題をクリアできる。
#           - from A.B import ... によって import A が拡張されるというのはわかりづらい。
#           - ていうか一見して読めない。
#           - でも参照する時 A.B.C.D って書きたい!
import A.B.C

print(A.B.C.D)  # -> <function D at 0x10a6384c0>
print(A.B.C.E)  # -> <function E at 0x10a6385e0>

# import A.B.C.D  # -> ModuleNotFoundError: No module named 'A.B.C.D'
#                 # これはダメ。こういう import の仕方のときは、いちばん右は
#                 # 関数はダメで、モジュール名じゃないといけない。
# print(A.B.C.D)
