#!/bin/sh
source /etc/profile
app=$1

function getpid()
{
pid=`ps ajxf | grep 'python3' | grep $app | awk '{print $3}' | uniq`
echo $pid
}

function restartapp()
{
num=$1
((n=$n+1))
logname='/tmp/MO_'$app'_'$num'.log'
`ps ajxf | grep 'python3' | grep $app | awk '{print $2}' | xargs kill -9`
nohup python3 $app >> $logname &
echo $logname
}


n=0
logname='/tmp/MO_'$app'_'$n'.log'
while true
pid=$(getpid)
do
if [ "`echo $pid | wc -L`" = "0" ]
then
logname=$(restartapp $n)
#nohup python3 $app >> $logname &
fi

uptime=`stat -c %Y $logname`
runtime=`date +%s`
((dt=$runtime-$uptime))
echo $logname:$pid:$uptime,$runtime,$dt

if [ "$dt" -gt "300" ]
then
echo going to restart $app ...
logname=$(restartapp $n)
#ps ajxf | grep 'python3' | grep $app | awk '{print $3}' | xargs kill -9
#nohup python3 $app >> $logname &
fi

sleep 300
done
