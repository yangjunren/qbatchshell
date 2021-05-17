# -*- coding: utf-8 -*-

from qiniu import Auth
from qiniu import BucketManager
import logging

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


def _filter_suffix(file_path, i, fileType, suffix):
    if ";" in suffix:
        suffix_tuple = tuple(suffix.split(";"))
        if str(i.get("key")).endswith(suffix_tuple) and str(i.get("mimeType")) in fileType:
            _write_file(file_path, i)
    else:
        if str(i.get("key")).endswith(suffix) and str(i.get("mimeType")) in fileType:
            _write_file(file_path, i)


def _filter_fsize(file_path, i, fileType, suffix, fsize):
    """过滤大小为0的文件"""
    if fsize:
        if i.get("fsize") == 0:
            _write_file(file_path, i)
    else:
        _filter_filetype_suffix(file_path, i, fileType, suffix)


def _filter_Storagetype(file_path, i, fileType, suffix, fsize, stype):
    if stype == -1:
        _filter_fsize(file_path, i, fileType, suffix, fsize)
    elif stype == 0:
        if i.get("type") == 0:
            _filter_fsize(file_path, i, fileType, suffix, fsize)
    elif stype == 1:
        if i.get("type") == 1:
            _filter_fsize(file_path, i, fileType, suffix, fsize)
    elif stype == 2:
        if i.get("type") == 2:
            _filter_fsize(file_path, i, fileType, suffix, fsize)


def _filter_filetype_suffix(file_path, i, fileType, suffix):
    """根据文件类型/文件名后缀 过滤文件"""
    if fileType and suffix:
        _filter_suffix(file_path, i, fileType, suffix)
    elif fileType and suffix is None:
        if str(i.get("mimeType")) in fileType:
            _write_file(file_path, i)
    elif fileType is None and suffix:
        _filter_suffix(file_path, i, fileType, suffix)
    else:
        _write_file(file_path, i)


def _filter_listinfo(ret, file_path, start=None, end=None, fileType=None, suffix=None, fsize=False, stype=-1):
    for i in ret.get("items")[1:]:
        putTime = str(i.get("putTime"))[:10]
        if start and end is None:
            if putTime > start:
                _filter_Storagetype(file_path, i, fileType, suffix, fsize, stype)
        elif end and start is None:
            if putTime < end:
                _filter_Storagetype(file_path, i, fileType, suffix, fsize, stype)
        elif start and end:
            _filter_Storagetype(file_path, i, fileType, suffix, fsize, stype)
        else:
            _filter_Storagetype(file_path, i, fileType, suffix, fsize, stype)


def _list(access_key, secret_key, bucket_name, file_path, prefix, start, end, fileType, suffix, limit=1000,
          delimiter=None,
          marker=None, fsize=False, stype=-1):
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    if eof:
        marker = None
        _filter_listinfo(ret, file_path, start, end, fileType, suffix, fsize, stype)
    else:
        if info.status_code == 200:
            marker = ret.get("marker")
    return ret, marker, info


def listBucket(access_key, secret_key, bucket, file_path, prefix=None, start=None, end=None, fileType=None,
               suffix=None, fsize=False, stype=-1):
    ret, marker, info = _list(access_key, secret_key, bucket, file_path, prefix=prefix, start=start, end=end,
                              fileType=fileType, suffix=suffix, fsize=fsize, stype=stype)
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
                                              prefix=prefix, start=start, end=end, fileType=fileType, suffix=suffix,
                                              fsize=fsize, stype=stype)
            marker = marker_new
        except Exception as e:
            logger.wran(e)
            raise e
