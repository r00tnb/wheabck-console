<?php
//global: $pwd, $path, $sign, $data
//$sign 为整数取值0,1,2。0无具体含义，1代表文件存在不询问直接覆盖，2代表此次上传数据需要添加到指定文件尾部
$ret = 0;
chdir($pwd);
if(!file_exists($path) || $sign>0){
    $f = false;
    if($sign == 1 || $sign == 0){
        $f = fopen($path, 'wb');
    }else if($sign == 2 && file_exists($path)){
        $f = fopen($path, 'ab');
    }
    if($f === false){
        $ret = -1;
    }else{
        fwrite($f, $data);
        fclose($f);
        $ret = 1;
    }
}
echo $ret;