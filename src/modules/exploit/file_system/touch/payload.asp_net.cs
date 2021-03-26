using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;

public class Payload
{

    public string Run()
    {
        Directory.SetCurrentDirectory(Global.pwd);
        DateTime mtime = GetDateTime(Global.mtime);
        DateTime atime = GetDateTime(Global.atime);
        if (!File.Exists(Global.file) && !Directory.Exists(Global.file))
        {
            using(File.Create(Global.file));
        }
        Directory.SetCreationTime(Global.file, mtime);
        Directory.SetLastAccessTime(Global.file, atime);
        Directory.SetLastWriteTime(Global.file, mtime);
        return "1";
    }

    DateTime GetDateTime(object timeStamp)
    {
        if(timeStamp == null) return DateTime.Now;
        DateTime dtStart = new DateTime(1970, 1, 1).ToUniversalTime();
        long lTime = long.Parse(timeStamp + "0000000");
        TimeSpan toNow = new TimeSpan(lTime);
        DateTime targetDt = dtStart.Add(toNow);
        return targetDt.ToLocalTime();
    }
}