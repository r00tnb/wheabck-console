<?php
//global: $pwd, $infile, $outfile
chdir($pwd);
if(file_exists($infile)){
    $f=fopen($infile, "r");
    flock($f, LOCK_EX);
    unlink($infile);
    flock($f, LOCK_UN);
}
if(file_exists($outfile)){
    $f=fopen($outfile, "r");
    flock($f, LOCK_EX);
    unlink($outfile);
    flock($f, LOCK_UN);
}