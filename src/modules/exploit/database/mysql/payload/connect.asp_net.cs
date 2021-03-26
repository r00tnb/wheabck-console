using System;
using System.Web;
using System.IO;
using System.Text;
using MySql.Data;
using MySql.Data.MySqlClient;
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
    public string Run()
    {
        ret = new Ret();
        MySqlConnection conn = Connect();
        if(ret.code == 1){
            conn.Close();
        }
        return Global.json_encode(ret);
    }

    MySqlConnection Connect(){
        MySqlConnectionStringBuilder builder = new MySqlConnectionStringBuilder();
        builder["Server"] = Global.host+","+Global.port;
        builder["Database"] = Global.database;
        builder["Uid"] = Global.user;
        builder["Pwd"] = Global.password;
        builder["Connect Timeout"] = 10;
        MySqlConnection conn = new MySqlConnection(builder.ConnectionString);
        try{
            conn.Open();
        }catch(Exception e){
            ret.code = -1;
            ret.msg = Convert.ToBase64String(Encoding.UTF8.GetBytes(e.ToString()));
        }
        return conn;
    }
}