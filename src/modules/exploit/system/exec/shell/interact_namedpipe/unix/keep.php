<?php
//global: $outpipe, $inpipe, $pwd
ignore_user_abort(true);
set_time_limit(0);
chdir($pwd);
if(function_exists('posix_mkfifo') && !file_exists($inpipe) && !file_exists($outpipe)){
    if(!posix_mkfifo($inpipe, 0777) || !posix_mkfifo($outpipe, 0777))
        die("-1");
    else{
        chmod($inpipe, 0777);
        chmod($outpipe, 0777);
    }
}
$out = fopen($outpipe, "rb");
$in = fopen($inpipe, "wb");
while(file_exists($inpipe) && file_exists($outpipe)){
    sleep(1);
}
@fclose($out);
@fclose($in);
echo "1";