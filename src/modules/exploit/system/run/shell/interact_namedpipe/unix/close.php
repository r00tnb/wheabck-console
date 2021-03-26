<?php
//global: $outpipe, $inpipe, $pwd
chdir($pwd);
if(file_exists($outpipe))
    unlink($outpipe);
if(file_exists($inpipe))
    unlink($inpipe);
