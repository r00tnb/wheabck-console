<?php
//global: $pwd, $flist
$ret = array('code'=>1, 'msg'=>array());
chdir($pwd);
function deldir($d, array& $ret){
    if(is_dir($d)){
        $dir = opendir($d);
        if($dir === false){
            $ret['code'] = -1;
            $ret['msg'][] = base64_encode("Directory `{$d}` open failed!");
        }
        while(($file=readdir($dir)) !== false){
            if($file == "." || $file == "..") continue;
            if(is_dir($file)){
                deldir($d.DIRECTORY_SEPARATOR.$file, $ret);
            }elseif(!unlink($file)){
                $ret['code'] = -1;
                $ret['msg'][] = base64_encode("File `{$file}` delete failed!");
            }else{
                $ret['msg'][] = base64_encode("File `{$file}` delete successfully!");
            }
        }
        if(rmdir($d))
            $ret['msg'][] = base64_encode("Directory `{$d}` delete successfully!");
        else{
            $ret['code'] = -1;
            $ret['msg'][] = base64_encode("Directory `{$d}` delete failed!");
        }
    }
}

$flist = explode("\n", $flist);
foreach($flist as $file){
    if(!$file) continue;
    if(is_dir($file)){
        deldir($file, $ret);
    }elseif(file_exists($file)){
        if(!unlink($file)){
            $ret['code'] = -1;
            $ret['msg'][] = base64_encode("File `{$file}` delete failed!");
        }else{
            $ret['msg'][] = base64_encode("File `{$file}` delete successfully!");
        }
    }else{
        $ret['code'] = -1;
        $ret['msg'][] = base64_encode("File `{$file}` is not exist!");
    }
}
echo json_encode($ret);