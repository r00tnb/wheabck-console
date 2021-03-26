using System;
using System.Web;
using System.IO;
using System.Text;
using System.Runtime.Serialization;
using System.Security.AccessControl;
using System.Collections;
using System.Security.Principal;


public class Payload
{
    [KnownType(typeof(ArrayList))]
    [DataContract]
    class Ret
    {

        [DataMember]
        public int code = 1;

        [DataMember]
        public ArrayList msg = new ArrayList();
    }
    Ret ret;
    public string Run()
    {
        ret = new Ret();
        Directory.SetCurrentDirectory(Global.pwd);
        if (File.Exists(Global.path))
        {
            ret.msg.Add(GetFileInfo(Global.path));
        }
        else if (Directory.Exists(Global.path))
        {
            DirectoryInfo directory = new DirectoryInfo(Global.path);
            foreach (FileInfo f in directory.GetFiles())
            {
                ret.msg.Add(GetFileInfo(Path.Combine(Global.path, f.Name)));
            }
            foreach (DirectoryInfo d in directory.GetDirectories())
            {
                ret.msg.Add(GetDirectoryInfo(Path.Combine(Global.path, d.Name)));
            }
        }
        else
        {
            ret.code = -1;
        }
        return Global.json_encode(ret);
    }

    ArrayList GetFileInfo(string path)
    {
        ArrayList info = new ArrayList();
        FileInfo fileInfo;
        FileSecurity fileSecurity;
        try{
            fileInfo = new FileInfo(path);
            fileSecurity = fileInfo.GetAccessControl();
        }catch(Exception){
            info.Add("-r--------");
            info.Add("(Unknown)");
            info.Add("(Unknown)");
            info.Add(0);
            info.Add(0);
            info.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(Path.GetFileName(path))));
            return info;
        }
        string owner = fileSecurity.GetOwner(typeof(NTAccount)).ToString();
        string group;
        try{
            group = fileSecurity.GetGroup(typeof(NTAccount)).ToString();
        }catch(Exception){
            group = "(Unknown)";
        }
        info.Add(GetPermissions(fileSecurity.GetAccessRules(true, true,
                                typeof(SecurityIdentifier)), owner, group, true));
        info.Add(owner);
        info.Add(group);
        info.Add(fileInfo.Length);
        DateTime startTime = new System.DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
        info.Add((long)(fileInfo.LastWriteTimeUtc - startTime).TotalSeconds);
        info.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(fileInfo.Name)));
        return info;
    }

    ArrayList GetDirectoryInfo(string path)
    {
        ArrayList info = new ArrayList();
        DirectoryInfo fileInfo;
        DirectorySecurity fileSecurity;
        try{
            fileInfo = new DirectoryInfo(path);
            fileSecurity = fileInfo.GetAccessControl();
        }catch(Exception){
            info.Add("d---------");
            info.Add("(Unknown)");
            info.Add("(Unknown)");
            info.Add(0);
            info.Add(0);
            info.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(Path.GetFileName(path))));
            return info;
        }
        string owner = fileSecurity.GetOwner(typeof(NTAccount)).ToString();
        string group;
        try{
            group = fileSecurity.GetGroup(typeof(NTAccount)).ToString();
        }catch(Exception){
            group = "(Unknown)";
        }
        info.Add(GetPermissions(fileSecurity.GetAccessRules(true, true,
                                typeof(SecurityIdentifier)), owner, group, false));
        info.Add(owner);
        info.Add(group);
        info.Add(0);
        DateTime startTime = new System.DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
        info.Add((long)(fileInfo.LastWriteTimeUtc - startTime).TotalSeconds);
        info.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(fileInfo.Name)));
        return info;
    }

    string GetPermissions(AuthorizationRuleCollection accessRules, string owner, string group, bool isfile)
    {
        if (accessRules.Count == 0) return isfile ? "-rwxrwxrwx" : "drwxrwxrwx";
        string info_owner = "---", info_group = "---", info_other = "---";
        foreach (FileSystemAccessRule rule in accessRules)
        {
            string tmp = rule.IdentityReference.Translate(typeof(NTAccount)).ToString();
            if (tmp == owner)
            {
                info_owner = perms(rule);
            }
            if (tmp == group)
            {
                info_group = perms(rule);
            }
            if (tmp == WindowsIdentity.GetCurrent().Name)
            {
                info_other = perms(rule);
            }

        }
        return (isfile?"-":"d")+info_owner+info_group+info_other;
    }

    string perms(FileSystemAccessRule rule)
    {
        char[] info = new char[]{'-', '-', '-'};
        if (rule.AccessControlType == AccessControlType.Allow)
        {
            string tmp0 = rule.FileSystemRights.ToString();
            if (tmp0.Contains("Read")) info[0] = 'r';
            if (tmp0.Contains("Write")) info[1] = 'w';
            if (tmp0.Contains("Execute")) info[2] = 'x';
            if (tmp0.Contains("FullControl"))
            {
                info[0] = 'r';
                info[1] = 'w';
                info[2] = 'x';
            }
        }
        return new string(info);
    }
}