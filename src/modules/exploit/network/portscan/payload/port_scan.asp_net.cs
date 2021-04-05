using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Collections;
using System.Net.Sockets;
using System.Net;
using System.Collection.Generic;
using System.Threading;

public class Payload
{
    ManualResetEvent TimeoutObj = new ManualResetEvent(false);

    public string Run()
    {
        Dictionary<int, string> ret = new Dictionary<int, string>()
        EndPoint point = new IPEndPoint(IPAddress.Any, 0);
        foreach (string p in Global.ports.Split(new char[] { ',' }))
        {
            byte[] buf = new byte[1024];
            int port = int.Parse(p);
            if (Global.isudp)
            {
                try
                {
                    Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
                    sock.ReceiveTimeout = Global.timeout;
                    sock.SendTo(new byte[] { 0x44 }, new IPEndPoint(IPToLong(Global.ip), port));
                    sock.ReceiveFrom(buf, ref point);
                    ret.Add(port, Convert.ToBase64String(buf));
                }
                catch
                {
                    continue;
                }
            }
            else
            {
                try
                {
                    Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                    TimeoutObj.Reset();
                    sock.BeginConnect(Global.ip, port, CallBackMethod, sock);
                    if(TimeoutObj.WaitOne(Global.timeout, false)){
                        if(sock.Connected){
                            sock.
                            ret.Add(port, Convert.ToBase64String(buf));
                        }   
                    }
                    sock.Shutdown(SocketShutdown.Both);
                    sock.Close();
                }
                catch(Exception e)
                {
                    continue;
                }
            }
        }
        return Global.json_encode(ret);
    }

    void CallBackMethod(IAsyncResult asyncresult)
    {
        //使阻塞的线程继续 
        TimeoutObj.Set();
        Socket sock = (Socket)asyncresult.AsyncState;
        try{
            sock.EndConnect(asyncresult);
        }catch(SocketException e){

        }
    }

    long IPToLong(string ip)
    {
        string[] items = ip.Split(new char[] { '.' });
        return long.Parse(items[3]) << 24
            | long.Parse(items[2]) << 16
            | long.Parse(items[1]) << 8
            | long.Parse(items[0]);
    }
}