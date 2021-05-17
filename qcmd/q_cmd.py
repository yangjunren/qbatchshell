# -*- coding: utf-8 -*-
from threading import Thread
from six import text_type
from argparse import ArgumentParser
import os, shutil, sys, logging, lmdb

global res

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from qcmd import qcmd_global
from qcmd.listbucket import listBucket
from qcmd.bmodtype import Batch_modtype
from qcmd.bchstatus import Batch_chstatus

_version = qcmd_global.Version

logger = logging.getLogger("qcmd")
fs_coding = sys.getfilesystemencoding()

config_path = ""


def to_printable_str(s):
    if isinstance(s, text_type):
        return s.encode(fs_coding)
    else:
        return s


def account_config(name, accesskey, secretkey):
    try:
        env = lmdb.open("./.account")
        txn = env.begin(write=True)
        txn.put(name.encode(), "{0}:{1}".format(accesskey, secretkey).encode())
        txn.commit()
        env.close()
        if os.path.exists(".old_account.json"):
            os.remove(".old_account.json")
        elif os.path.exists(".account.json"):
            shutil.copy("./.account.json", "./.old_account.json")
        with open(".account.json", "w") as f:
            f.write("{0}:{1}:{2}".format(name, accesskey, secretkey))
        logger.debug('qcmd login successfully')
    except Exception as e:
        raise e


def qcmd_account(config_path, name, accesskey, secretkey):
    qcmd_config_path = os.path.expanduser(config_path)
    if not os.path.exists(qcmd_config_path):
        os.makedirs(qcmd_config_path)
    try:
        os.chdir(qcmd_config_path)
        if name and accesskey and secretkey:
            account_config(name, accesskey, secretkey)
        elif (name and accesskey and secretkey) is "":
            if os.path.exists(".account.json"):
                with open(".account.json", "r") as f:
                    l = f.read().split(":")
                    return print("Name:{0}\naccesskey:{1}\nsecretkey:{2}".format(l[0], l[1], l[2]))
            else:
                logger.warn("Login please enter \"qcmd account -h\" for help")
        else:
            logger.warn("Parameter error, please enter \"qcmd account -h\" for help")
    except Exception as e:
        raise e


def qcmd_user_list():
    env = lmdb.open("./.qcmd/.account")
    txn = env.begin()
    ret = ""
    for key, value in txn.cursor():
        value_list = value.decode().split(":")
        ret1 = "\nName:{0}\naccesskey:{1}\nsecretkey:{2}\n".format(key.decode(), value_list[0], value_list[1])
        ret = ret + ret1
    env.close()
    return ret


def qcmd_user_cu(name):
    env = lmdb.open("./.qcmd/.account")
    txn = env.begin()
    val = txn.get(name.encode()).decode()
    re = val.split(":")
    os.chdir("./.qcmd")
    account_config(name, re[0], re[1])
    ret = "\nName:{0}\naccesskey:{1}\nsecretkey:{2}\n".format(name, re[0], re[1])
    env.close()
    return ret


def qcmd_user_remove(name):
    env = lmdb.open("./.qcmd/.account")
    txn = env.begin(write=True)
    txn.delete(name.encode())
    txn.commit()
    env.close()


def qcmd_thread():
    global res
    res = -1
    desc = """Qiniu commandline tool for managing your bucket and CDN"""
    parser = ArgumentParser(description=desc)
    parser.add_argument('-c', '--config_path', help="Specify config_path", type=str, default="./.qcmd")
    parser.add_argument('-d', '--debug', help="Debug mode", action="store_true", default=False)
    parser.add_argument('-l', '--log_path', help="Specify log_path", type=str, default="./.qcmd")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + _version)

    sub_parser = parser.add_subparsers()
    parser_account = sub_parser.add_parser("account", help="Get/Set AccessKey and SecretKey")
    parser_account.add_argument("-ak", "--accesskey", help="your accessKey", type=str, required=False, default="")
    parser_account.add_argument("-sk", "--secretkey", help="your secretkey", type=str, required=False, default="")
    parser_account.add_argument("-n", "--name", help="username", type=str, required=False, default="")
    parser_account.set_defaults(func=Qcmd.account)

    parser_user = sub_parser.add_parser("user", help="Manage users")
    parser_user_group = parser_user.add_mutually_exclusive_group(required=True)
    parser_user_group.add_argument("-cu", help="Change user to AccountName", type=str)
    parser_user_group.add_argument("-ls", action="store_const", const="list")
    parser_user_group.add_argument("-remove", help="Remove user UID from inner db", type=str)
    parser_user.set_defaults(func=Qcmd.user)

    parser_listbucket = sub_parser.add_parser("listbucket", help="List all the files in the bucket")
    parser_listbucket.add_argument("-b", "--bucket", help="bucket name", required=True, type=str)
    parser_listbucket.add_argument("-o", "--outfile", help="output file", required=True, type=str)
    parser_listbucket.add_argument("-p", "--prefix", help="list by prefix", type=str, default=None)
    parser_listbucket.add_argument("-s", "--start", help="start timeStamp", type=str, default=None)
    parser_listbucket.add_argument("-e", "--end", help="end timeStamp", type=str, default=None)
    parser_listbucket.add_argument("-ft", "--fileType", help="file mimeType", type=str, default=None)
    parser_listbucket.add_argument("-sf", "--suffix", help="file suffix", type=str, default=None)
    parser_listbucket.add_argument("--fsize", help="fsize", type=bool, default=False)
    parser_listbucket.add_argument("--stype", help="storage type", type=int, default=-1)
    parser_listbucket.set_defaults(func=Qcmd.list_bucket)

    parser_bmodtype = sub_parser.add_parser("bmodtype", help="Batch modify file storage type")
    parser_bmodtype.add_argument("-b", "--bucket", help="bucket name", required=True, type=str)
    parser_bmodtype.add_argument("-i", "--inputfile", help="input file", required=True, type=str)
    parser_bmodtype.add_argument("-s", "--successfile", help="change storage type success file list", type=str,
                                 default=None)
    parser_bmodtype.add_argument("-f", "--failurefile", help="change storage type failure file list", type=str,
                                 default=None)
    parser_bmodtype.add_argument("-tc", "--threadcount", help="multiple thread count", type=int,
                                 default=3)
    parser_bmodtype.add_argument("-S", "--sep", help="separator", type=str, default=",")
    parser_bmodtype.set_defaults(func=Qcmd.batch_modtype)

    parser_chstatus = sub_parser.add_parser("bchstatus", help="Batch modify file status")
    parser_chstatus.add_argument("-b", "--bucket", help="bucket name", required=True, type=str)
    parser_chstatus.add_argument("-i", "--inputfile", help="input file", required=True, type=str)
    parser_chstatus.add_argument("-s", "--successfile", help="change storage type success file list", type=str,
                                 default=None)
    parser_chstatus.add_argument("-f", "--failurefile", help="change storage type failure file list", type=str,
                                 default=None)
    parser_chstatus.add_argument("-tc", "--threadcount", help="multiple thread count", type=int,
                                 default=3)
    parser_chstatus.add_argument("-S", "--sep", help="separator", type=str, default=",")
    parser_chstatus.set_defaults(func=Qcmd.batch_chstatus)

    args = parser.parse_args()
    try:
        res = args.func(args)
        return res
    except Exception:
        return 0


class Qcmd(object):

    @staticmethod
    def account(args):
        if not config_path:
            conf_path = args.config_path
        else:
            conf_path = config_path
        try:
            accesskey = args.accesskey
            secretkey = args.secretkey
            name = args.name
            qcmd_account(conf_path, name, accesskey, secretkey)
        except Exception as e:
            logger.warn(e)
            return "qcmd account failed"

    @staticmethod
    def user(args):
        try:
            if args.cu:
                ret = qcmd_user_cu(args.cu)
                return print(ret)
            if args.ls:
                ret = qcmd_user_list()
                return print(ret)
            elif args.remove:
                qcmd_user_remove(args.remove)
            else:
                return print("Parameter error, please enter \"qcmd user -h\" for help")
        except Exception as e:
            raise e

    @staticmethod
    def list_bucket(args):
        try:
            if os.path.exists("./.qcmd/.account.json"):
                with open("./.qcmd/.account.json", "r") as f:
                    ret = f.read().split(":")
                    accesskey = ret[1]
                    secretkey = ret[2]
                bucket_name = args.bucket
                outfile = args.outfile
                prefix = args.prefix
                start = args.start
                end = args.end
                fileType = args.fileType
                suffix = args.suffix
                fsize = args.fsize
                stype = args.stype
                listBucket(accesskey, secretkey, bucket_name, outfile, prefix, start, end, fileType, suffix, fsize,
                           stype)
            else:
                return print("Login please enter \"qcmd account -h\" for help")
        except Exception as e:
            logger.warn(e)
            raise e

    @staticmethod
    def batch_modtype(args):
        try:
            if os.path.exists("./.qcmd/.account.json"):
                with open("./.qcmd/.account.json", "r") as f:
                    ret = f.read().split(":")
                    accesskey = ret[1]
                    secretkey = ret[2]
                bucket_name = args.bucket
                inputfile = args.inputfile
                successfile = args.successfile
                failurefile = args.failurefile
                threadcount = args.threadcount
                sep = args.sep
                Batch = Batch_modtype(accesskey, secretkey, bucket_name, inputfile, sep, successfile, failurefile,
                                      threadcount)
                Batch.b_modtype()
            else:
                return print("Login please enter \"qcmd account -h\" for help")
        except Exception as e:
            logger.warn(e)
            raise e

    @staticmethod
    def batch_chstatus(args):
        try:
            if os.path.exists("./.qcmd/.account.json"):
                with open("./.qcmd/.account.json", "r") as f:
                    ret = f.read().split(":")
                    accesskey = ret[1]
                    secretkey = ret[2]
                bucket_name = args.bucket
                inputfile = args.inputfile
                successfile = args.successfile
                failurefile = args.failurefile
                threadcount = args.threadcount
                sep = args.sep
                Batch = Batch_chstatus(accesskey, secretkey, bucket_name, inputfile, sep, successfile, failurefile,
                                       threadcount)
                Batch.batch_chstatus()
        except Exception as e:
            logger.warn(e)
            raise e


def main_thread():
    mainthread = Thread()
    mainthread.start()
    thread_ = Thread(target=qcmd_thread)
    thread_.start()
    import time
    try:
        while True:
            time.sleep(1)
            if thread_.is_alive() is False:
                break
    except KeyboardInterrupt:
        mainthread.stop()
        thread_.stop()
        sys.exit()


def _main():
    thread_ = Thread(target=main_thread)
    thread_.daemon = True
    thread_.start()
    try:
        while thread_.is_alive():
            thread_.join(2)
    except KeyboardInterrupt:
        logger.info('exiting')
        return 1
    global res
    return res


if __name__ == '__main__':
    _main()
    global res
    sys.exit(res)
