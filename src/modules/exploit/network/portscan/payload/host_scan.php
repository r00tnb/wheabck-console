<?php
//global: $hosts, $timeout
//使用UDP检测主机是否存活
$ret = array();
$hosts = explode(",", $hosts);
$port = 30000;
foreach ($hosts as $host) {
    $sock = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
    socket_set_option($sock, SOL_SOCKET, SO_RCVTIMEO, array("sec"=>$timeout/1000, "usec" => 0));
    if(socket_connect($sock, $host, $port) && socket_send($sock, "123", 3, 0) !== false){
        $r = socket_recvfrom($sock, $buf, 1024, 0, $host, $port);
        $errcode = socket_last_error($sock);
        if($r !== false || $errcode==SOCKET_ECONNREFUSED || $errcode==SOCKET_ECONNRESET ||$errcode==SOCKET_ECONNABORTED) $ret[] = $host;
    }
    socket_close($sock);
}
echo json_encode($ret);
