<?php
$info = array(
    'host'=>$_SERVER['HTTP_HOST'],
    'pwd'=>__DIR__,
    'user'=>'', 
    'group'=>'',
    'domain'=>'',
    'os_type'=>PHP_OS, 
    'tmpdir'=>sys_get_temp_dir(),
    'sep'=>DIRECTORY_SEPARATOR
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

foreach($info as $k=>$v){
    $info[$k] = base64_encode($v);
}
echo json_encode($info);