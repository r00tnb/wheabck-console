<?php
//global: $pwd, $file, $atime, $mtime
chdir($pwd);
if($atime === null) $atime = time();
if($mtime === null) $mtime = time();
if(touch($file, $mtime, $atime) === false) echo -1;
echo 1;