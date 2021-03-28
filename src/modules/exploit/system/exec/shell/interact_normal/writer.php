<?php
//global: $infile, $pwd, $cmd
chdir($pwd);
if(file_exists($infile)){
    $in = fopen($infile, "wb");
    flock($in, LOCK_EX);
    fwrite($in, $cmd);
    flock($in, LOCK_UN);
    fclose($in);
}else{
    die("-1");
}
echo "1";