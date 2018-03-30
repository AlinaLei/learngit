<?php
/**
 * 发送消息到企业微信号监控
 * author: harold
 * Date: 2017/3/2
 * Time: 11:27
 */
//namespace Qywechat;

class Qywechat
{

    protected static $CropID = '';
    protected static $Secret = '';
    protected static $agentid  = 0;
    protected static $touser = 0;
    protected static $toparty = 0;
    protected static $totag = 0;

    /**
     * 发送消息到企业微信号中
     * @param string $message 需要发送的消息
     * @param string $environ 发送环境：production为喂车车企业号中的后台质量监控应用，test为测试的企业号告警机器人
     * @return mixed
     * @author harold
     */
    public static function alert($message='',$environ='production')
    {
       // $environ = $environ ? trim($environ) : (empty(ENVIRON) ? 'production' : ENVIRON);
//        $environ = empty(ENVIRON) ? ($environ ? trim($environ) : 'production') : ENVIRON;
        $environ = 'production';
	if($environ=='production'){
            self::$CropID = 'wx19c3544e9bc08452';
            self::$Secret='OIOb43M2-Li5r7QG3d_42js0C6fuviHg2ZFL5HHvY_z5EAIiJVrsE1dx-K5jZ4KM';
//            self::$Secret = 'vjMUiZuBRno7ZGdvbv65PgHzCYx0Mm4leufq6vUolJ0';
            self::$agentid = '78';
            self::$toparty = '0';
            self::$touser = '0';
            self::$totag = '4';
        }else{
            self::$CropID='wx563239a87604a702';
            self::$Secret='VP6GZiZ69eM13CrF3m0Nza3vePpqMO5JI7HS-MNGaXSy-YU6deHe6nNH4xBI_PHC';
            self::$agentid = '1';
            self::$toparty = '1';
            self::$touser = '0';
            self::$totag = '0';
        }
        $access_token = self::get_access_token(self::$CropID,self::$Secret);

        $message = $message ? trim($message) : '测试使用PHP脚本发送消息';
        $result = self::send_qyweixin_message($access_token,$message);
        if(strpos($result,'{')!==0){
            return false;
        }
        $result = json_decode($result,1);
        if(empty($result) || !is_array($result)){
            return false;
        }
        return $result;
    }

    /**
     * 发送消息到微信企业号
     * @author harold
     * @param string $access_token 发送消息需带上token
     * @param string $message 消息内容
     * @param int    $toparty 发送给指定群组
     * @param string $totag 发送到指定tag标签的用户
     * @param string $touser 发送到指定用户
     */
    protected static function send_qyweixin_message($access_token,$message)
    {
        //通过access_token发送消息
        $PURL = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=$access_token";
        if(empty($access_token)){
            die('access token is not valid');
        }
        if(empty($message)){
            die('send message is not valid');
        }
        if(empty(self::$toparty) && empty(self::$totag) && empty(self::$touser)){
            die('toparty or totag or touse must set one');
        }
        $send_data = [
            'msgtype' => 'text',
            'agentid' => self::$agentid,
            'text' => [
                'content' => $message
            ],
//            'safe' => 0
        ];
        if(!empty(self::$toparty)){
            $send_data['toparty'] = self::$toparty;
        }
        if(!empty(self::$totag)){
            $send_data['totag']  = self::$totag;//发送到指定tag标签的用户
        }
        if(!empty(self::$touser)){
            $send_data['touser'] = self::$touser;//发送到指定用户
        }
        $json_data = json_encode(
            $send_data,
            JSON_UNESCAPED_UNICODE //若发送中文则不可省略
        );
//        echo $json_data;
        try {
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $PURL);
            curl_setopt($ch, CURLOPT_TRANSFERTEXT, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $json_data);
            curl_setopt($ch, CURLOPT_HEADER, false);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 5); // 5秒超时
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            $res = curl_exec($ch);
            if(curl_error($ch) || curl_errno($ch)){
                throw new \Exception(curl_error($ch));
            }
            curl_close($ch);
            return $res;
        }catch (\Exception $exception){
            print($exception->getMessage());
            exit;
        }
    }

    /**
     * 获取访问token
     * @author harold
     * @return string $access_token 调用企业微信API的token
     */
    protected static function get_access_token($CropID,$Secret)
    {
        $GURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=$CropID&corpsecret=$Secret";

        try{
            //获取token
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $GURL);
            curl_setopt($ch, CURLOPT_HEADER, false);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            $res = curl_exec($ch);
            if(curl_error($ch) || curl_errno($ch)){
                throw new \Exception(curl_error($ch));
            }
            curl_close($ch);
            $res = json_decode($res,1);
            return $res['access_token'];
        }catch (\Exception $exception){
            print($exception->getMessage());
            exit;
        }
    }

    /**
     * 获取访问token
     * @return string $access_token 调用企业微信API的token
     */
    /**
     * curl请求数据
     * @param string $url 请求地址
     * @param array $data 请求数据
     * @return mixed
     * @author harold
     */
    function curl_get($url,$data=[])
    {

        try{
            //获取token
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_HEADER, false);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            if(!empty($data)){
                curl_setopt($ch, CURLOPT_POST, 1);
                curl_setopt($ch, CURLOPT_POSTFIELDS,$data);
            }
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            $res = curl_exec($ch);
            if(curl_error($ch) || curl_errno($ch)){
                throw new \Exception(curl_error($ch));
            }
            curl_close($ch);
            $res = json_decode($res,1);
            return $res;
        }catch (\Exception $exception){
            print($exception->getMessage());
            exit;
        }
    }

}


$obj = new Qywechat();
$options = getopt('m:');
$obj->alert( $options['m'] );

