r'''Upload a local file to server.
'''

from api.exploit import WebshellExploit, Cmdline
from api.webshell import WebshellSession, Webshell
from api import logger, config, utils
import argparse
import base64
import tempfile
import os
import json
import re
import math

class exploit(WebshellExploit):

    def __init__(self):
        super().__init__()
        self.parse = argparse.ArgumentParser(prog="upload", description="Upload a local file to server.")
        self.parse.add_argument('local', help="A file on local.")
        self.parse.add_argument('remote', help="A file on server.", nargs='?', default=None)
        self.parse.add_argument('-f', '--force', help="If the remote file exists, it will be overwritten without asking.")
        self.parse.add_argument('-s', '--uploadsize', help="Set the data size limit for each upload.You can use k, m, etc. to set the size, setting 0 will not limit the size of the data uploaded each time.Such as 1024, 1024b, 1024k, etc. are all valid", 
            type=self._getsize, default="0")
        self.help = __doc__ + self.parse.format_help()

    def _getsize(self, size: str)-> int:
        '''用于转换传入的--uploadsize参数
        '''
        size = size.strip().rstrip('bB').lower()
        try:
            util = size[-1]
            if util not in 'km':
                return int(size)

            size = float(size[:-1])
            if util == 'k':
                size *= 1024
            elif util == 'm':
                size *= 1024*1024
            return int(size)
        except Exception as e:
            logger.error("Upload size parameter format error!(You can set like 1024, 1232k, 2131M, 0 etc.)")
            raise e

    def support(self, session:WebshellSession)-> bool:
        '''判断当前命令是否支持指定的session， 一般来说session即为运行命令时的session
        '''
        self.session = session
        return isinstance(self.session, WebshellSession) and self.session.server_info.lang in (Webshell.PHP, Webshell.ASP_NET_CS, )

    def run(self, args:Cmdline)-> int:
        args = self.parse.parse_args(args.options)
        local = os.path.join(config.work_path, args.local)
        if not os.path.isfile(local):
            logger.error(f"Local file `{local}` is not a file!")
            return self.STOP
        
        data = b''
        with open(local, 'rb') as f:
            data = f.read()
        remote = args.remote
        if remote is None:
            remote = os.path.split(local)[1]
        if remote.endswith('/') or remote.endswith('\\'):
            remote += os.path.split(local)[1]
        logger.info('Uploading...')
        return self._upload(remote, data, False if args.force is None else args.force, args.uploadsize)

    def _upload(self, remote:str, data:bytes, force: bool, uploadsize: int)->int:
        '''将数据写入到远程文件
        '''
        sign = 1 if force else 0
        total = math.ceil(len(data)/uploadsize) if uploadsize > 0 else 1
        progress = 0
        while data:
            block = data[:uploadsize] if uploadsize > 0 else data
            data = data[uploadsize:] if uploadsize > 0 else b''
            ret = self.evalfile('upload', pwd=self.session.pwd, path=remote, data=block, sign=sign)
            sign = 2
            ret = ret.data
            while ret is None:
                if total>1:# 如果分片上传时失败，则重传一次该分片
                    ret = self.evalfile('upload', pwd=self.session.pwd, path=remote, data=block, sign=sign)
                    if ret.is_success():
                        ret = ret.data
                        break
                logger.error("upload file error!")
                return self.STOP
            if ret == '0':
                logger.warning(f"Remote file `{remote}` is exist.")
                if utils.input("Are you sure to overwrite the file? (y/n) ").lower() == 'y':
                    return self._upload(remote, block+data, True, uploadsize)
            elif ret == '-1':
                logger.error("Remote file open failed!")
                logger.error('Check if the path is correct or if you have write permission.')
                return self.STOP
            elif ret == '1':
                if total > 1:
                    progress += 1
                    per = str(int(progress/total*100))+'%'
                    per = per.rjust(4, ' ')
                    print(f"Upload progress {per} ({progress}/{total}).", end='\r', flush=True)
                continue
            else:
                logger.error("Unknow error!")
                return self.STOP
        logger.info(f"Upload file `{remote}` successfully!")
        return self.SUCCESS

    def docomplete(self, text: str)-> dict:# 本地文件路径补全
        result = []
        pre = ''
        match = re.compile(r'''^(upload +)([\w\-/\\.]*)$''', re.M).search(text)
        root = os.getcwd()
        if match:
            dirname, name = os.path.split(match.group(2))
            path = os.path.join(root, dirname)
            pre = match.group(1)+os.path.join(dirname, 'a')[:-1]
            if os.path.exists(path) and os.path.isdir(path):
                for filename in os.listdir(path):
                    if os.path.isdir(os.path.join(path, filename)):
                        filename += os.sep
                    else:
                        filename += ' '
                    if filename.startswith(name):
                        result.append(filename)

        return {'pre':pre, 'matchs':result}