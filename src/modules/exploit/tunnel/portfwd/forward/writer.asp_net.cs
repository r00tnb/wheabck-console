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
        string infile = Path.Combine(Path.GetTempPath(), Global.sessionid + "_in");
        if (File.Exists(infile))
        {
            Mutex mut = new Mutex(false, Global.sessionid + "_test123");
            try
            {
                mut.WaitOne();
                using (FileStream stream = File.Open(infile, FileMode.Append, FileAccess.Write))
                {
                    stream.Write(Global.writebuf, 0, Global.writebuf.Length);
                }
            }catch(Exception){return "-1";}finally{mut.ReleaseMutex();}

            return "1";
        }
        return "-1";
    }
}