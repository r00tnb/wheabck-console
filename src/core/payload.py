from src.core.base import Payload
import re
import base64

class PHPPayload(Payload):

    @property
    def code(self)-> bytes:
        result = self._code.decode()

        # 删除所有注释(无法处理字符串， 待改进)
        result = re.sub(r'//.*|/\*[\s\S]*\*/', '', result)

        # 删除标签和开始结尾的空白符
        result = re.sub(r'^\s*<\?php\s*|\s*\?>\s*$', '', result) 

        for k, v in self._global.items():
            result = f"${k} = {self.python_to_php(v)};\n" + result

        return result.encode()
    
    def python_to_php(self, var):
        '''将python变量映射到PHP变量
        '''
        if var is None:
            return "null"
        elif var is True:
            return "true"
        elif var is False:
            return "false"
        elif isinstance(var, (int, float)):
            return str(var)
        else: # 其他情况当字符串处理，并且对字符串进行编码，防止解析错误
            if not isinstance(var, bytes):
                var = str(var).encode()
            var = base64.b64encode(var).decode()
            return f"base64_decode('{var}')"

class CSharpPayload(Payload):

    # payload可以使用该类传递变量
    wrapper_code = r'''%(code)s

    public static class Global{
        %(var)s

        public static string json_encode(object obj){
            System.Runtime.Serialization.Json.DataContractJsonSerializer js = new System.Runtime.Serialization.Json.DataContractJsonSerializer(obj.GetType());
            System.IO.MemoryStream msObj = new System.IO.MemoryStream();
            js.WriteObject(msObj, obj);
            msObj.Position = 0;
            System.IO.StreamReader sr = new System.IO.StreamReader(msObj, System.Text.Encoding.UTF8);
            string json = sr.ReadToEnd();
            sr.Close();
            msObj.Close();
            return json;
        }
    }
    '''

    @property
    def code(self)-> bytes:
        result = self._code.decode()

        # 删除所有注释(无法处理字符串， 待改进)
        result = re.sub(r'//.*|/\*[\s\S]*\*/', '', result)

        # 删除标签和开始结尾的空白符
        result = re.sub(r'^\s*<\?php\s*|\s*\?>\s*$', '', result)

        cs_global = ''
        for k, v in self._global.items():
            t, v = self.python_to_cs(v)
            cs_global += f"public static {t} {k}={v};\n"

        result = CSharpPayload.wrapper_code % {'code':result, 'var':cs_global}

        return result.encode()
    
    def python_to_cs(self, var)-> tuple:
        '''将python变量映射到C#变量
        '''
        if var is None:
            return 'object', "null"
        elif var is True:
            return 'bool', "true"
        elif var is False:
            return 'bool', "false"
        elif isinstance(var, int):
            return 'int', str(var)
        elif isinstance(var, float):
            return 'double', str(var)
        elif isinstance(var, str):
            var = base64.b64encode(var.encode()).decode()
            return 'string', f'System.Text.Encoding.UTF8.GetString(System.Convert.FromBase64String("{var}"))'
        else: # 其他情况当字节流处理，并且对字符串进行编码，防止解析错误
            if not isinstance(var, bytes):
                var = str(var).encode()
            var = base64.b64encode(var).decode()
            return 'byte[]', f'System.Convert.FromBase64String("{var}")'