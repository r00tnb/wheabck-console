from urllib import request, parse
from http.client import HTTPResponse
import ssl
ssl._create_default_https_context = ssl._create_unverified_context # 全局忽略https证书校验

class HttpException(Exception):

    def __init__(self, code: int, msg: str, response: HTTPResponse):
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.response = response

class HttpErrorHandler(request.HTTPErrorProcessor):

    def http_response(self, request, response:HTTPResponse):
        if response.code >= 500:
            raise HttpException(500, "500 error!", response)
        return response

    https_response = http_response

class Request:

    def __init__(self):

        cookie_handler = request.HTTPCookieProcessor()
        error_handler = HttpErrorHandler()
        proxy_handler = request.ProxyHandler({})
        self._opener = request.build_opener(cookie_handler, proxy_handler, error_handler)

        self._default_headers = {
            "User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        }

    def reuqest(self, url: str, method: str="POST", data=None, headers: dict=None, timeout: float=0, params: dict=None)->HTTPResponse:
        if isinstance(data, dict):
            data = parse.urlencode(data).encode()

        if headers is None:
            headers = {}
            headers.update(self._default_headers)
        else:
            tmp = {}
            tmp.update(self._default_headers)
            tmp.update(headers)
            headers = tmp
        
        if params is not None:
            tmpurl = parse.urlsplit(url)
            query = parse.parse_qsl(tmpurl.query)
            for k, v in params.items():
                query.append((k, v))
            url = parse.urlunsplit([tmpurl.scheme, tmpurl.netloc, tmpurl.path, parse.urlencode(query), ''])

        req = request.Request(url, data, headers, method=method)
        return self._opener.open(req, timeout=None if timeout == 0 else timeout)
    
    def get(self, url: str, params: dict=None, headers: dict=None, timeout: float=None)->HTTPResponse:
        return self.reuqest(url, "GET", headers=headers, timeout=timeout, params=params)

    def post(self, url: str, data: dict=None, headers: dict=None, timeout: float=None)->HTTPResponse:
        return self.reuqest(url, "POST", headers=headers, timeout=timeout, data=data)

    def update_header(self, key: str, value: str):
        '''更新默认的请求头部，同名覆盖，不同名则新建
        '''
        key = str(key)
        value = str(value)
        self._default_headers[key] = value
