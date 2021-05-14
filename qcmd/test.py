# # import os
# # import pytest
# #
# # def test_account():
# #     os.system("python3 setup.py install")
# #     ret = os.system("python3 qcmd/q_cmd.py account")
# #     print(ret)
# import lmdb
#
# env = lmdb.open("./00")
# txt = env.begin(write=True)
# txt.put("name".encode(), "ces".encode())
# print(txt.get("name".encode()).decode())

# a = ""
# b = ""
# if (a and b) is "":
#     with open("../.qcmd/.account.json", "r") as f:
#         l = f.read().split(":")
#         print("ess:{0}\nde".format(l[2]))
#
# else:
#     print("1")
# import lmdb
#
# env = lmdb.open("../.qcmd/.account")
# txn = env.begin(write = True)
# # for key, value in txn.cursor():
# #     # print(key)
# #     # print(value)
# #     value_list = value.decode().split(":")
# #     print("Name:{0}\naccesskey:{1}\nsecretkey:{2}\n".format(key.decode(), value_list[0], value_list[1]))
# ret = txn.delete("212".encode())
# txn.commit()
# print(ret)
# txn.commit()

# a = "1610270469"
# b = "1610270468"
# c = a > b
# print(c)

# a = [1, 2, 3]
# b = [4, 5, 6]
#
# # for i in a:
# #     for j in b:
# #         print(j * i)
#
# ret = [i * j for j in b for i in a]
# print(ret)

# a = (".py", ".mp4", ".jpg")
# a = ".py;.mp4;.jpg;"
# a1 = tuple(a.split(";"))
# # a = [i for i in a.split(";")]
# b = "123"
# print(b.endswith(a1))
import os

"""
dirpath：string，是当前目录的路径；
dirnames：list， 是当前路径下所有的子文件夹名字；
filenames：list， 是当前路径下所有的非目录子文件的名字。
"""
# # print(os.listdir("../.qcmd"))
# filepath = ""
# for dirpath, dirnames, filenames in os.walk(filepath, topdown=False):
#     for name in filenames:
#         print(os.path.join(dirpath, name).split(filepath)[1])
#     # for name in dirs:
#     #     print(os.path.join(root, name))


with open("../list.txt", "r") as f:
    ret = tuple(f.readlines())
    for i in ret:
        print(i)