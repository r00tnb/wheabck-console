using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload
{
    public string Run()
    {
        string ret = "1";
        Directory.SetCurrentDirectory(Global.pwd);
        if (!Directory.Exists(Global.path))
        {
            Directory.CreateDirectory(Global.path);
        }else{
            ret = "-1";
        }
        return ret;
    }
}