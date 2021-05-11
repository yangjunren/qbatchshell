# -*- coding: utf-8 -*-

from qiniu import Auth
from qiniu import BucketManager
import logging, lmdb

logger = logging.getLogger("qcmd")


def _write_file(file_path, i):
    """写入列举信息"""
    for key, value in i.items():
        with open(file_path, "a+") as f:
            if key == "key":
                f.writelines(str(value) + ",")
            elif key == "fsize":
                f.writelines(str(value) + ",")
            elif key == "mimeType":
                f.writelines(str(value) + ",")
            elif key == "putTime":
                f.writelines(str(value)[:10] + ",")
            elif key == "type":
                f.writelines(str(value) + ",")
            elif key == "status":
                f.writelines(str(value) + "\n")


def _filter_filetype_suffix(file_path, i, fileType, suffix):
    """根据文件类型和文件名后缀过滤文件"""
    if fileType and suffix:
        if str(i.get("key")).endswith(suffix) and str(i.get("mimeType")) == fileType:
            _write_file(file_path, i)
    elif fileType and suffix is None:
        if str(i.get("mimeType")) == fileType:
            _write_file(file_path, i)
    elif fileType is None and suffix:
        if str(i.get("key")).endswith(suffix):
            _write_file(file_path, i)
    else:
        _write_file(file_path, i)


def _filter_listinfo(ret, file_path, start=None, end=None, fileType=None, suffix=None):
    for i in ret.get("items")[1:]:
        putTime = str(i.get("putTime"))[:10]
        if start and end is None:
            if putTime > start:
                _filter_filetype_suffix(file_path, i, fileType, suffix)
        elif end and start is None:
            if putTime < end:
                _filter_filetype_suffix(file_path, i, fileType, suffix)
        elif start and end:
            _filter_filetype_suffix(file_path, i, fileType, suffix)
        else:
            _filter_filetype_suffix(file_path, i, fileType, suffix)


def _list(access_key, secret_key, bucket_name, file_path, prefix, start, end, fileType, suffix, limit=1000,
          delimiter=None,
          marker=None):
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    if eof:
        marker = None
        _filter_listinfo(ret, file_path, start, end, fileType, suffix)
    else:
        if info.status_code == 200:
            marker = ret.get("marker")
    return ret, marker, info


def listBucket(access_key, secret_key, bucket, file_path, prefix=None, start=None, end=None, fileType=None,
               suffix=None):
    ret, marker, info = _list(access_key, secret_key, bucket, file_path, prefix=prefix, start=start, end=end,
                              fileType=fileType, suffix=suffix)
    while True:
        try:
            if info.status_code != 200:
                return print(
                    "{0},Please check accesskey and secretkey.\nLogin please enter \"qcmd account -h\" for help".format(
                        info.text_body))
            elif marker is None and info.status_code == 200:
                return print("listbucket success")
            else:
                ret, marker_new, info = _list(access_key, secret_key, bucket, marker=marker, file_path=file_path,
                                              prefix=prefix, start=start, end=end, fileType=fileType, suffix=suffix)
            marker = marker_new
        except Exception as e:
            logger.wran(e)
            raise e


if __name__ == '__main__':
    with open("../.qcmd/.account.json", "r") as f:
        ret = f.read().split(":")
    accesskey = ret[1]
    secretkey = ret[2]
    bucket_name = "upload30"
    listfile = "./list.txt"
    start = "1619606052"
    listBucket(accesskey, secretkey, bucket_name, listfile, start=start)
