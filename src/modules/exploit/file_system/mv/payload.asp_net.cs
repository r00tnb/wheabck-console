using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload{

    public string Run(){
        Directory.SetCurrentDirectory(Global.pwd);
        if(File.Exists(Global.source)){
            if(File.Exists(Global.dest) && !Global.f){
                return "Dest file exists";
            }
            File.Copy(Global.source, Global.dest, true);
            File.Delete(Global.source);
        }else{
            return "Souce file not exists!";
        }
        return "ok";
    }
}