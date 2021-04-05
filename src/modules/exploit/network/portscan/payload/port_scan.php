<?php
//global: $ports, $ip, $isudp, $timeout
$ret = array();
$ports = explode(",", $ports);
$timeout = $timeout/1000;
foreach($ports as $port){
    $port = intval($port);
    if($isudp){
        $sock = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
        socket_set_option($sock,SOL_SOCKET, SO_RCVTIMEO, array("sec"=>intval($timeout), "usec"=>0));
        if(socket_sendto($sock, "hello\r\n", 3, 0, $ip, $port)!==false && socket_recvfrom($sock, $buf, 1024, 0, $ip, $port)!==false) $ret[$port] = base64_encode($buf);
        socket_close($sock);
    }else{
        $res = fsockopen($ip, $port, $errno, $errstr, 2);
        if($res !== false){
            stream_set_blocking($res, false);
            fwrite($res, "hello\r\n");
            fflush($res);
            $read = array($res);
            $w = $ee = array();
            if(stream_select($read, $w, $e, intval($timeout))){
                $data = '';
                foreach($read as $r){
                    $data = fread($r, 1024);
                    break;
                }
                $ret[$port] = base64_encode($data);
            }else{
                $ret[$port] = "";
            }
            fclose($res);
        }
    }
}
echo json_encode($ret);