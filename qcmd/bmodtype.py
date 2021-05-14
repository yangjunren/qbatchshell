# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth
from qiniu import BucketManager
import os, sys, time
import logging

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from qcmd.q_threadpool import SimpleThreadPool
from qcmd.util import to_unicode

logger = logging.getLogger("qcmd")


class Batch_modtype(object):
    def __init__(self, access_key, secret_key, bucket_name, inputfile, successfile=None,
                 failurefile=None, thread_count=3):
        self.access_key = access_key
        self.secret_key = secret_key
        self._inner_threadpool = SimpleThreadPool(3)
        self.thread_count = thread_count
        self.inputfile = inputfile
        self.bucket_name = bucket_name
        self.successfile = successfile
        self.failurefile = failurefile

    def mod_type(self, bucket_name, key, storage_type, successfile, failurefile):
        try:
            q = Auth(self.access_key, self.secret_key)
            bucket = BucketManager(q)
            # 2表示归档存储，1表示低频存储，0是标准存储
            _, info = bucket.change_type(bucket_name, key, storage_type)
            return key, info, successfile, failurefile
        except Exception as e:
            logger.warn(to_unicode(e))
            time.sleep(0.01)

    def read_inputfile(self, inputfile):
        with open(inputfile, "r") as f:
            ret = tuple(f.readlines())
        return ret

    def b_modtype(self):
        self._inner_threadpool = SimpleThreadPool(self.thread_count)
        inputfile_list = self.read_inputfile(self.inputfile)
        for i in inputfile_list:
            if "\n" in i:
                i = i.replace("\n", "")
            _i = i.split(",")
            _key = _i[0]
            _storage_type = _i[1]
            try:
                self._inner_threadpool.add_task(self.mod_type, self.bucket_name, _key, _storage_type, self.successfile,
                                                self.failurefile)
            except Exception as e:
                logger.warn(to_unicode(e))
        self._inner_threadpool.wait_completion()
        result = self._inner_threadpool.get_result()
        return print(result)


if __name__ == '__main__':
    access_key = "*****"
    secret_key = "*****"
    bucket_name = "*****"
    inputfile = "******"
    successfile = None
    Batch = Batch_modtype(access_key, secret_key, bucket_name, inputfile, successfile)
    ret = Batch.b_modtype()
    print(ret)
