function FindProxyForURL(url, host)
{
   var proxyHost="172.16.10.71";
   var httpProxyPort="808";
   var ftpProxyPort="2121";
   var sslProxyPort="808";
   var gopherProxyPort="808";
   var socksProxyPort="1080";
   var telnetProxyPort="23";
   var newsProxyPort="119";

   if (isPlainHostName(host) || isInNet(host, "127.0.0.0", "255.255.255.0")){
   	return "DIRECT";
   }

   if (url.substring(0, 5) == "http:") {
	return "PROXY "+proxyHost+":"+httpProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
   }
   if (url.substring(0, 4) == "ftp:") {
   	return "PROXY "+proxyHost+":"+ftpProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
   }
   if (url.substring(0, 7) == "gopher:") {
	return "PROXY "+proxyHost+":"+gopherProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
   }
   if (url.substring(0, 6) == "https:") {
	return "PROXY "+proxyHost+":"+sslProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
   }
   if (url.substring(0, 6) == "telnet:") {
	return "PROXY "+proxyHost+":"+telnetProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
   }
   if (url.substring(0, 6) == "news:") {
	return "PROXY "+proxyHost+":"+newsProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
   }
   return "PROXY "+proxyHost+":"+httpProxyPort+"; SOCKS "+proxyHost+":"+socksProxyPort+"; DIRECT";
}
