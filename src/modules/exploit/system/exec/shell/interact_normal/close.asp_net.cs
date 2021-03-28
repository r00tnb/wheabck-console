using System;
using System.Web;
using System.IO;
using System.Text;
using System.Threading;
using System.Runtime.Serialization;

public class Payload{
    public string Run(){
        Directory.SetCurrentDirectory(Global.pwd);
        Mutex mut = new Mutex(false, "test123");
        mut.WaitOne();
        if(File.Exists(Global.infile)){
            File.Delete(Global.infile);
        }
        if(File.Exists(Global.outfile)){
            File.Delete(Global.outfile);
        }
        mut.ReleaseMutex();
        return "";
    }
}