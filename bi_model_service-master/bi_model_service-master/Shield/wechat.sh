CropID='wx19c3544e9bc08452'
Secret='OIOb43M2-Li5r7QG3d_42js0C6fuviHg2ZFL5HHvY_z5EAIiJVrsE1dx-K5jZ4KM'
GURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=$CropID&corpsecret=$Secret"
Gtoken=$(/usr/bin/curl -s -G $GURL | awk -F\" '{print $10}')

PURL="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=$Gtoken"

function body() {
        local int AppID=78                        #企业号中的应用id
        #local UserID=$1                         # 部门成员id，zabbix中定义的微信接收者
        #local PartyID=1                         # 部门id，定义了范围，组内成员都可接收到消息
        local tagID=4                         # tagid，定义了范围，tag成员都可接收到消息
        local Msg=$(echo "$@" | cut -d" " -f3-) # 过滤出zabbix传递的第三个参数
        printf '{\n'
        #printf '\t"touser": "'"$UserID"\"",\n"
        #printf '\t"toparty": "'"$PartyID"\"",\n"
        printf '\t"totag": "'"$tagID"\"",\n"
        printf '\t"msgtype": "text",\n'
        printf '\t"agentid": "'"$AppID"\"",\n"
        printf '\t"text": {\n'
        printf '\t\t"content": "'"$Msg"\""\n"
        printf '\t},\n'
        printf '\t"safe":"0"\n'
        printf '}\n'
}
/usr/bin/curl --data-ascii "$(body $1 $2 $3)" $PURL
