<?php
//global: $inpipe, $pwd, $cmd
chdir($pwd);
if(file_exists($inpipe)){
    $in = @fopen($inpipe, 'wb');
    fwrite($in, $cmd);
    fclose($in);
}else{
    die("-1");
}
echo "1";