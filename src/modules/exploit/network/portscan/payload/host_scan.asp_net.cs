using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Collections;
using System.Net.Sockets;
using System.Net;

public class Payload{

    public string Run(){
        ArrayList ret = new ArrayList();
        int port = 30000;
        byte[] buf = new byte[1024];
        EndPoint point = new IPEndPoint(IPAddress.Any, 0);
        foreach(string ip in Global.hosts.Split(new char[]{','})){
            try{
                Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
                sock.ReceiveTimeout = Global.timeout;
                sock.Connect(ip, port);
                sock.Send(new byte[]{0x44});
                sock.ReceiveFrom(buf, ref point);
            }catch(SocketException e){
                if(e.SocketErrorCode == SocketError.ConnectionRefused 
                    || e.SocketErrorCode == SocketError.ConnectionReset
                    || e.SocketErrorCode == SocketError.ConnectionAborted){
                    ret.Add(ip);
                }
                continue;
            }catch{
                continue;
            }
            ret.Add(ip);
        }
        return Global.json_encode(ret);
    }

    long IPToLong(string ip){
        string[] items = ip.Split(new char[]{'.'});
        return long.Parse(items[3]) << 24
            | long.Parse(items[2]) << 16
            | long.Parse(items[1]) << 8
            | long.Parse(items[0]);
    }
}