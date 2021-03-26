using System;
using System.Web;
using System.IO;
using System.Text;
using System.Threading;

public class Payload{
    public string Run(){
        HttpContext.Current.Server.ScriptTimeout = 180;
        string signfile = Path.Combine(Path.GetTempPath(), Global.sessionid+"_sign");
        while(!File.Exists(signfile)){
            Thread.Sleep(200);
        }
        return "1";
    }
}